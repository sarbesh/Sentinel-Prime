// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Sentinel Prime - eBPF Packet Capture Module
 * High-performance network flow capture with minimal overhead
 * Captures 5-tuple flow data with size and timing metadata
 */

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_FLOWS 65536
#define FLOW_TIMEOUT_SEC 1
#define ETH_P_IP 0x0800
#define ETH_P_IPV6 0x86DD
#define IPPROTO_TCP 6
#define IPPROTO_UDP 17
#define IPPROTO_ICMP 1
#define IPPROTO_ICMPV6 58

/* Flow key - 5-tuple identifier */
struct flow_key {
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u8 protocol;
    __u8 pad[3];
};

/* Flow statistics - aggregated per 1-second window */
struct flow_stats {
    __u64 packet_count;
    __u64 byte_count;
    __u64 first_seen;
    __u64 last_seen;
    __u32 window_start;
};

/* Flow metadata for userspace */
struct flow_event {
    struct flow_key key;
    __u32 window_start;
    __u32 window_end;
    __u64 packet_count;
    __u64 byte_count;
    __u8 interface_index;
    __u8 flags;
    __u8 pad[2];
};

/* Flow aggregation map - stores in-kernel flow state */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_FLOWS);
    __type(key, struct flow_key);
    __type(value, struct flow_stats);
} flow_aggregator SEC(".maps");

/* PERF_EVENT_ARRAY - sends aggregated flows to userspace */
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} flow_events SEC(".maps");

/* Configuration map for runtime parameters */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u32);
} config_map SEC(".maps");

/* Helper to extract flow key from IPv4 packet */
static __always_inline int extract_ipv4_key(struct __sk_buff *skb, 
                                            __u32 offset,
                                            struct flow_key *key)
{
    __u8 protocol;
    
    if (bpf_skb_load_bytes(skb, offset + 9, &protocol, 1) < 0)
        return -1;
    
    key->protocol = protocol;
    
    /* Load src and dst IP (offset 12 and 16 in IPv4 header) */
    if (bpf_skb_load_bytes(skb, offset + 12, &key->src_ip, 4) < 0)
        return -1;
    if (bpf_skb_load_bytes(skb, offset + 16, &key->dst_ip, 4) < 0)
        return -1;
    
    /* Extract ports for TCP/UDP */
    if (protocol == IPPROTO_TCP || protocol == IPPROTO_UDP) {
        __u16 src_port, dst_port;
        __u32 ip_header_len;
        
        /* Get IP header length from first byte */
        __u8 ihl;
        if (bpf_skb_load_bytes(skb, offset, &ihl, 1) < 0)
            return -1;
        ip_header_len = (ihl & 0x0F) * 4;
        
        if (bpf_skb_load_bytes(skb, offset + ip_header_len, &src_port, 2) < 0)
            return -1;
        if (bpf_skb_load_bytes(skb, offset + ip_header_len + 2, &dst_port, 2) < 0)
            return -1;
        
        key->src_port = bpf_ntohs(src_port);
        key->dst_port = bpf_ntohs(dst_port);
    } else if (protocol == IPPROTO_ICMP) {
        /* For ICMP, use type and code as pseudo-ports */
        __u8 icmp_type, icmp_code;
        __u32 ip_header_len;
        __u8 ihl;
        
        if (bpf_skb_load_bytes(skb, offset, &ihl, 1) < 0)
            return -1;
        ip_header_len = (ihl & 0x0F) * 4;
        
        if (bpf_skb_load_bytes(skb, offset + ip_header_len, &icmp_type, 1) < 0)
            return -1;
        if (bpf_skb_load_bytes(skb, offset + ip_header_len + 1, &icmp_code, 1) < 0)
            return -1;
        
        key->src_port = icmp_type;
        key->dst_port = icmp_code;
    } else {
        key->src_port = 0;
        key->dst_port = 0;
    }
    
    return 0;
}

/* Main packet capture program attached to TC ingress/egress */
SEC("tc")
int capture_packet(struct __sk_buff *skb)
{
    __u16 eth_proto;
    __u32 offset = 0;
    struct flow_key key = {};
    struct flow_stats *stats;
    struct flow_stats new_stats = {};
    __u64 now = bpf_ktime_get_ns();
    __u32 window_start = now / 1000000000ULL;  /* 1-second windows */
    
    /* Skip if packet too small */
    if (skb->len < 14)
        return TC_ACT_OK;
    
    /* Parse Ethernet header */
    if (bpf_skb_load_bytes(skb, 12, &eth_proto, 2) < 0)
        return TC_ACT_OK;
    eth_proto = bpf_ntohs(eth_proto);
    offset = 14;
    
    /* Only process IPv4 for now (simpler, faster) */
    if (eth_proto != ETH_P_IP)
        return TC_ACT_OK;
    
    /* Extract 5-tuple flow key */
    if (extract_ipv4_key(skb, offset, &key) < 0)
        return TC_ACT_OK;
    
    /* Create normalized key (sort by IP to group bidirectional flows) */
    if (key.src_ip > key.dst_ip) {
        __u32 tmp_ip = key.src_ip;
        __u16 tmp_port = key.src_port;
        key.src_ip = key.dst_ip;
        key.dst_ip = tmp_ip;
        key.src_port = key.dst_port;
        key.dst_port = tmp_port;
    }
    
    /* Look up or create flow entry */
    stats = bpf_map_lookup_elem(&flow_aggregator, &key);
    
    if (stats) {
        /* Update existing flow */
        __sync_fetch_and_add(&stats->packet_count, 1);
        __sync_fetch_and_add(&stats->byte_count, skb->len);
        stats->last_seen = now;
    } else {
        /* Create new flow entry */
        new_stats.packet_count = 1;
        new_stats.byte_count = skb->len;
        new_stats.first_seen = now;
        new_stats.last_seen = now;
        new_stats.window_start = window_start;
        
        bpf_map_update_elem(&flow_aggregator, &key, &new_stats, BPF_ANY);
    }
    
    return TC_ACT_OK;
}

/* Timer callback - flushes aggregated flows to userspace every second */
SEC("tp/sched/sched_process_exit")
int flush_timer(void *ctx)
{
    struct flow_key zero_key = {};
    struct flow_key *key = &zero_key;
    struct flow_stats *stats;
    struct flow_event event = {};
    __u64 now = bpf_ktime_get_ns();
    __u32 current_window = now / 1000000000ULL;
    
    /* Iterate through all flows and flush completed windows */
    while ((key = bpf_map_get_next_key(&flow_aggregator, key, &event.key)) == 0) {
        stats = bpf_map_lookup_elem(&flow_aggregator, &event.key);
        if (!stats)
            continue;
        
        /* Only flush if window has ended */
        if (stats->window_start < current_window) {
            event.window_start = stats->window_start;
            event.window_end = stats->window_start + 1;
            event.packet_count = stats->packet_count;
            event.byte_count = stats->byte_count;
            event.interface_index = 0;  /* Will be set by userspace per-interface */
            event.flags = 0;
            
            /* Send to userspace via perf buffer */
            bpf_perf_event_output(ctx, &flow_events, BPF_F_CURRENT_CPU, 
                                  &event, sizeof(event));
            
            /* Reset flow stats for next window */
            stats->packet_count = 0;
            stats->byte_count = 0;
            stats->window_start = current_window;
            stats->first_seen = now;
        }
    }
    
    return 0;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";