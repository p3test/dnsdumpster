#!/usr/bin/env python3

import requests
import time
import argparse
import json
import sys
import os

BASE_URL = "https://api.dnsdumpster.com/domain/"

def get_domain_info(api_key, domain, page=None, include_map=False):
    headers = {"X-API-Key": api_key}
    params = {}
    if page:
        params["page"] = page
    if include_map:
        params["map"] = 1

    url = f"{BASE_URL}{domain}"
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 429:
            print("Request limit exceeded. Waiting 2 seconds and trying again...")
            time.sleep(2)
            return get_domain_info(api_key, domain, page, include_map)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[!] Error while requesting {domain}: {e}")
        return None

def print_summary(domain, data):
    print(f"\n======= {domain.upper()} =======")
    if not data:
        print("No data to display.")
        return

    print("\nA records:")
    for record in data.get("a", []):
        host = record["host"]
        for ip_info in record["ips"]:
            print(f"  - Host: {host}, IP: {ip_info['ip']}, ASN: {ip_info['asn_name']}, Country: {ip_info['country']}")

    print("\nNS records:")
    for record in data.get("ns", []):
        host = record["host"]
        for ip_info in record["ips"]:
            print(f"  - Host: {host}, IP: {ip_info['ip']}, Country: {ip_info['country']}")

    print("\nTXT records:")
    for txt in data.get("txt", []):
        print(f"  - {txt}")

def save_result(domain, data):
    json_filename = f"{domain}.json"
    short_filename = f"short_{domain}.txt"
    try:
        # Save full JSON data
        with open(json_filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] Full results saved to: {json_filename}")
    except IOError as e:
        print(f"[!] Error saving {json_filename}: {e}")

    try:
        # Save short format with hostnames
        with open(short_filename, 'w') as f:
            a_records = data.get("a", [])
            for record in a_records:
                host = record.get("host", domain)
                for ip_info in record.get("ips", []):
                    ip = ip_info.get("ip", "")
                    f.write(f"{host} : {ip}\n")
        print(f"[+] Short results saved to: {short_filename}")
    except IOError as e:
        print(f"[!] Error saving {short_filename}: {e}")

def process_domain(api_key, domain):
    data = get_domain_info(api_key, domain)
    print_summary(domain, data)
    if data:
        save_result(domain, data)

def main():
    parser = argparse.ArgumentParser(description="Query DNSDumpster API for domain information")
    parser.add_argument('-k', '--key', required=True, help='Dnsdumpster API key')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--domain', help='Single domain to search')
    group.add_argument('-f', '--file', help='File with list of domains')

    args = parser.parse_args()

    if args.domain:
        process_domain(args.key, args.domain)
    elif args.file:
        if not os.path.isfile(args.file):
            print(f"[!] File not found: {args.file}")
            sys.exit(1)
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        for domain in domains:
            process_domain(args.key, domain)
            time.sleep(2)  # Respect API rate limit

if __name__ == "__main__":
    main()
