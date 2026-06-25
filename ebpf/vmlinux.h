/* SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause */
#ifndef __VMLINUX_H__
#define __VMLINUX_H__

/* Minimal vmlinux.h subset for packet capture */
#include <linux/types.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/icmp.h>

#if defined(__TARGET_ARCH_x86)
struct pt_regs {
    unsigned long r15;
    unsigned long r14;
    unsigned long r13;
    unsigned long r12;
    unsigned long bp;
    unsigned long bx;
    unsigned long r11;
    unsigned long r10;
    unsigned long r9;
    unsigned long r8;
    unsigned long ax;
    unsigned long cx;
    unsigned long dx;
    unsigned long si;
    unsigned long di;
    unsigned long orig_ax;
    unsigned long ip;
    unsigned long cs;
    unsigned long flags;
    unsigned long sp;
    unsigned long ss;
};
#elif defined(__TARGET_ARCH_arm64)
struct pt_regs {
    unsigned long regs[31];
    unsigned long sp;
    unsigned long pc;
    unsigned long pstate;
};
#endif

struct __sk_buff {
    __u32 len;
    __u32 pkt_type;
    __u32 mark;
    __u32 queue_mapping;
    __u32 protocol;
    __u16 vlan_proto;
    __u16 vlan_tci;
    __u32 priority;
    __u32 ingress_ifindex;
    __u32 ifindex;
    __u32 cb[5];
    __u32 family;
    __u32 remote_port;
    __u32 local_port;
    __u32 data;
    __u32 data_end;
    __u32 napi_id;
};

#define TC_ACT_OK 0
#define TC_ACT_UNSPEC (-1)

static inline __u16 bpf_ntohs(__u16 data) {
    return (data >> 8) | (data << 8);
}

static inline __u16 bpf_htons(__u16 data) {
    return (data << 8) | (data >> 8);
}

static inline __u32 bpf_ntohl(__u32 data) {
    return ((data & 0xff000000) >> 24) |
           ((data & 0x00ff0000) >> 8) |
           ((data & 0x0000ff00) << 8) |
           ((data & 0x000000ff) << 24);
}

/* BPF helper declarations */
extern void *bpf_map_lookup_elem(void *map, const void *key) = (void *) 1;
extern int bpf_map_update_elem(void *map, const void *key, const void *value, __u64 flags) = (void *) 2;
extern int bpf_map_delete_elem(void *map, const void *key) = (void *) 3;
extern int bpf_probe_read(void *dst, __u32 size, const void *unsafe_ptr) = (void *) 4;
extern __u64 bpf_ktime_get_ns(void) = (void *) 5;
extern int bpf_trace_printk(const char *fmt, ...) = (void *) 6;
extern __u32 bpf_get_prandom_u32(void) = (void*) 7;
extern int bpf_skb_load_bytes(const void *skb, __u32 off, void *to, __u32 len) = (void *) 26;
extern int bpf_perf_event_output(void *ctx, void *map, __u64 flags, void *data, __u32 size) = (void *) 25;
extern void *bpf_map_get_next_key(void *map, const void *key, void *next_key) = (void *) 8;

/* BPF_MAP_F_NO_PREALLOC */
#define BPF_F_NO_PREALLOC (1U << 0)
/* BPF_F_NUMA_NODE */
#define BPF_F_NUMA_NODE (1U << 1)
/* BPF_F_CURRENT_CPU */
#define BPF_F_CURRENT_CPU (~(0ULL))
/* BPF_ANY */
#define BPF_ANY 0
/* BPF_EXIST */
#define BPF_EXIST 1
/* BPF_NOEXIST */
#define BPF_NOEXIST 2

/* Map types */
#define BPF_MAP_TYPE_HASH 1
#define BPF_MAP_TYPE_ARRAY 2
#define BPF_MAP_TYPE_PERF_EVENT_ARRAY 4

#endif