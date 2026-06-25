// Sentinel Prime eBPF Packet Capture Module
// High-performance network flow extraction with minimal overhead
// Compatible with Linux kernel 5.4+

#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/ipv6.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/icmp.h>

#define MAX_FLOWS 65536
#define FLOW_TIMEOUT_SEC 30

// Flow key structure (5-tuple)
struct flow_key {
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u8 protocol;
    __u8 pad;
};

// Flow statistics
struct flow_stats {
    __u64 packet_count;
    __u64 byte_count;
    __u64 first_seen;
    __u64 last_seen;
    __u32 src_ip;
    __u32 dst_ip;
    __u16 src_port;
    __u16 dst_port;
    __u8 protocol;
    __u8 flags;
};

// BPF Maps
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_FLOWS);
    __type(key, struct flow_key);
    __type(value, struct flow_stats);
} flow_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} events SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u64);
} config SEC(".maps");

// Helper function to extract flow key from packet
static __always_inline int extract_flow_key(struct __sk_buff *skb, struct flow_key *key, __u64 offset) {
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;
    
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return -1;
    
    __u16 proto = eth->h_proto;
    
    // Handle VLAN tagging
    if (proto == htons(ETH_P_8021Q)) {
        struct vlan_hdr *vlan = (void *)(eth + 1);
        if ((void *)(vlan + 1) > data_end)
            return -1;
        proto = vlan->h_vlan_encapsulated_proto;
        offset += sizeof(struct vlan_hdr);
    }
    
    // IPv4 handling
    if (proto == htons(ETH_P_IP)) {
        struct iphdr *iph = data + offset;
        if ((void *)(iph + 1) > data_end)
            return -1;
        
        if (iph->ihl * 4 > 20) {
            if ((void *)(iph) + iph->ihl * 4 > data_end)
                return -1;
        }
        
        key->src_ip = iph->saddr;
        key->dst_ip = iph->daddr;
        key->protocol = iph->protocol;
        
        __u32 ipihl = iph->ihl * 4;
        struct tcphdr *th = data + offset + ipihl;
        if ((void *)(th + 1) > data_end) {
            // Try UDP
            struct udphdr *uh = data + offset + ipihl;
            if ((void *)(uh + 1) > data_end)
                return -1;
            key->src_port = uh->source;
            key->dst_port = uh->dest;
        } else {
            if (key->protocol == IPPROTO_TCP) {
                key->src_port = th->source;
                key->dst_port = th->dest;
            } else if (key->protocol == IPPROTO_UDP) {
                struct udphdr *uh = data + offset + ipihl;
                if ((void *)(uh + 1) > data_end)
                    return -1;
                key->src_port = uh->source;
                key->dst_port = uh->dest;
            } else if (key->protocol == IPPROTO_ICMP) {
                struct icmphdr *icmph = data + offset + ipihl;
                if ((void *)(icmph + 1) > data_end)
                    return -1;
                key->src_port = icmph->type;
                key->dst_port = icmph->code;
            }
        }
        
        return 0;
    }
    
    // IPv6 handling (simplified)
    if (proto == htons(ETH_P_IPV6)) {
        struct ipv6hdr *iph6 = data + offset;
        if ((void *)(iph6 + 1) > data_end)
            return -1;
        
        // For simplicity, we'll skip IPv6 in this version
        // Can be added as needed
        
        return -1;
    }
    
    return -1;
}

// Main eBPF program - attached to network interface via TC
SEC("tc")
int tc_ingress(struct __sk_buff *skb) {
    struct flow_key key = {};
    __u64 offset = sizeof(struct ethhdr);
    
    if (extract_flow_key(skb, &key, offset) < 0)
        return TC_ACT_OK;
    
    // Get current timestamp
    __u64 now = bpf_ktime_get_ns();
    
    // Look up or create flow entry
    struct flow_stats *stats = bpf_map_lookup_elem(&flow_map, &key);
    if (stats) {
        // Update existing flow
        stats->packet_count++;
        stats->byte_count += skb->len;
        stats->last_seen = now;
    } else {
        // Create new flow
        struct flow_stats new_stats = {};
        new_stats.packet_count = 1;
        new_stats.byte_count = skb->len;
        new_stats.first_seen = now;
        new_stats.last_seen = now;
        new_stats.src_ip = key.src_ip;
        new_stats.dst_ip = key.dst_ip;
        new_stats.src_port = key.src_port;
        new_stats.dst_port = key.dst_port;
        new_stats.protocol = key.protocol;
        
        bpf_map_update_elem(&flow_map, &key, &new_stats, BPF_NOEXIST);
        
        // Send flow event to userspace via perf event
        bpf_perf_event_output(skb, &events, BPF_F_CURRENT_CPU, &key, sizeof(key));
    }
    
    return TC_ACT_OK;
}

// License and version
char _license[] SEC("license") = "GPL";
char _version[] SEC("version") = "1.0.0";