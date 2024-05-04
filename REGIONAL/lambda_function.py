import os
import boto3
import requests

def get_cloudflare_ips_v4():
    # Fetch the Cloudflare IPv4 list
    url_v4 = 'https://www.cloudflare.com/ips-v4/'
    response = requests.get(url_v4)
    if response.status_code == 200:
        ip_list_v4 = response.text.split()
        return ip_list_v4
    else:
        return []

def get_cloudflare_ips_v6():
    # Fetch the Cloudflare IPv6 list
    url_v6 = 'https://www.cloudflare.com/ips-v6/'
    response = requests.get(url_v6)
    if response.status_code == 200:
        ip_list_v6 = response.text.split()
        return ip_list_v6
    else:
        return []

def update_ip_set(ip_set_name, ip_set_id, ip_addresses):
    # Update the specified AWS WAFv2 IP set with the provided IP addresses
    try:
        # Create AWS WAFv2 client
        wafv2_client = boto3.client('wafv2')
        
        # Get the current state of the IP set by name
        response = wafv2_client.get_ip_set(
            Name=ip_set_name,
            Id=ip_set_id,
            Scope='REGIONAL'
        )
        
        # Extract LockToken and Id from the response
        ip_set = response['IPSet']
        lock_token = response['LockToken']
        ip_set_id = ip_set['Id']
        
        if not lock_token or not ip_set_id:
            raise ValueError("LockToken or Id not found in the IP set details.")
        
        # Update the IP set with new IP addresses
        wafv2_client.update_ip_set(
            Name=ip_set_name,
            Scope='REGIONAL',
            Id=ip_set_id,
            LockToken=lock_token,
            Addresses=ip_addresses
        )
        
        return f"IP addresses updated successfully for IP set: {ip_set_name}"
    except Exception as e:
        return f"Failed to update IP set: {ip_set_name}. Error: {str(e)}"

def lambda_handler(event, context):
    # Retrieve IP set names and IDs from environment variables
    ipv4_set_name = os.environ.get('IPV4_SET_NAME')
    ipv4_set_id = os.environ.get('IPV4_SET_ID')
    ipv6_set_name = os.environ.get('IPV6_SET_NAME')
    ipv6_set_id = os.environ.get('IPV6_SET_ID')
    
    # Fetch Cloudflare IPv4 addresses
    ip_addresses_v4 = get_cloudflare_ips_v4()
    if ip_addresses_v4:
        update_ip_set(ipv4_set_name, ipv4_set_id, ip_addresses_v4)
    else:
        print("No IPv4 addresses fetched from Cloudflare.")
    
    # Fetch Cloudflare IPv6 addresses
    ip_addresses_v6 = get_cloudflare_ips_v6()
    if ip_addresses_v6:
        update_ip_set(ipv6_set_name, ipv6_set_id, ip_addresses_v6)
    else:
        print("No IPv6 addresses fetched from Cloudflare.")

    return {
        'statusCode': 200,
        'body': "IP addresses updated successfully for IPv4 and IPv6 IP sets."
    }
