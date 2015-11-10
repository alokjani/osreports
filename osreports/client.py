#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright Reliance Jio Infocomm, Ltd.
#    Author: Alok Jani <Alok.Jani@ril.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import os
import sys
import argparse
import csv
from novaclient import client as novaclient
import cinderclient.v1.client as cinderclient
import keystoneclient.v2_0.client as keystoneclient
import swiftclient.client as swiftclient
import collections

# Print unicode text to the terminal
reload(sys)
sys.setdefaultencoding("utf-8")

# --
# Globals go here
#
os_username = None
os_password = None
os_auth_url = None
_debug = False

flavorListDefault = [
    'm1.tiny',
    'm1.small',
    'm1.medium',
    'm1.large',
    'm1.xlarge',
    'm1.2xlarge',
    'm1.4xlarge',
    'm1.8xlarge'
]


# --
# some helper functions
#
def load_creds_env():
    global os_username, os_password, os_auth_url
    os_username = os.environ['OS_USERNAME']
    os_password = os.environ['OS_PASSWORD']
    os_auth_url = os.environ['OS_AUTH_URL']


def get_keystone_creds():
    global os_username, os_password, os_auth_url
    if os_username == None or os_password == None or os_auth_url == None:
        load_creds_env()

    d = {}
    d['username'] = os_username
    d['password'] = os_password
    d['auth_url'] = os_auth_url
 #   d['tenant_name'] = os.environ['OS_TENANT_NAME']
    return d


def get_nova_creds():
    d = {}
    d['username']   = os.environ['OS_USERNAME']
    d['api_key']    = os.environ['OS_PASSWORD']
    d['auth_url']   = os.environ['OS_AUTH_URL']
    pass


def get_nova_client(p_tenant_name):
    return novaclient.Client("2",os_username, os_password, p_tenant_name, os_auth_url, service_type='compute')


def get_cinder_client(p_tenant_name):
    return cinderclient.Client(os_username, os_password, p_tenant_name, os_auth_url)


def get_keystone_client():
    creds = get_keystone_creds()
    return keystoneclient.Client(**creds)


def get_swift_client(p_tenant_name):
    return swiftclient.Connection(authurl=os_auth_url, user=os_username, key=os_password, tenant_name=p_tenant_name, auth_version='2')


# --
# get_flavor_count()
# Returns a flavor:count for a given tenant
#
def get_flavor_count(p_nova_client):
    instanceList = p_nova_client.servers.list()

    cnt_inst_flavor_distribution = {}
    cnt_inst_flavor_distribution['custom'] = 0

    global flavorListDefault
    for fname in flavorListDefault:
        cnt_inst_flavor_distribution[fname] = 0

    for inst in instanceList:
        t_inst_flav = inst.flavor['id']
        flavor = p_nova_client.flavors.get(t_inst_flav)

        if cnt_inst_flavor_distribution.has_key(flavor.name):
            cnt_inst_flavor_distribution[flavor.name] = cnt_inst_flavor_distribution[flavor.name] + 1
        else:
            cnt_inst_flavor_distribution['custom'] = cnt_inst_flavor_distribution['custom'] + 1

    return cnt_inst_flavor_distribution


# --
# get_instance_details()
# Returns vpcu, vmem, disk, floatingIP for a given tenant
#
def get_instance_details(p_nova_client):
    instanceList    = p_nova_client.servers.list()
    floatIpList     = p_nova_client.floating_ips.list()

    cnt_instances               = len(instanceList)
    cnt_instances_active        = 0
    cnt_vcpu                    = 0
    cnt_vcpu_active             = 0
    cnt_ram                     = 0
    cnt_ram_active              = 0
    cnt_disk                    = 0
    cnt_ephemeral               = 0
    cnt_floatip                 = len(floatIpList)
    cnt_floatip_disassociated   = 0

    for inst in instanceList:
        t_inst_flav = inst.flavor['id']

        flavor = p_nova_client.flavors.get(t_inst_flav)
        t_inst_vcpu = flavor.vcpus
        t_inst_ram  = flavor.ram
        t_inst_disk = flavor.disk
        t_inst_ephemeral = flavor.ephemeral

        cnt_vcpu = cnt_vcpu + t_inst_vcpu
        cnt_ram  = cnt_ram + t_inst_ram
        cnt_disk = cnt_disk + t_inst_disk
        cnt_ephemeral = cnt_ephemeral + t_inst_ephemeral

        if inst.status == "ACTIVE":
            cnt_instances_active = cnt_instances_active + 1
            cnt_vcpu_active = cnt_vcpu_active + t_inst_vcpu
            cnt_ram_active = cnt_ram_active + t_inst_ram

    for floatip in floatIpList:
        if floatip.instance_id == None:
            cnt_floatip_disassociated = cnt_floatip_disassociated + 1

    summary = {}
    summary['total_instances'] = cnt_instances
    summary['total_instances_active'] = cnt_instances_active
    summary['total_vcpu']   = cnt_vcpu
    summary['total_vcpu_active'] = cnt_vcpu_active

    summary['total_ram']    = cnt_ram
    summary['total_ram_active'] = cnt_ram_active

    summary['total_disk']   = cnt_disk
    summary['total_ephemeral'] = cnt_ephemeral
    summary['total_floatingip_allocated'] = cnt_floatip
    summary['total_floatingip_disassocated'] = cnt_floatip_disassociated

    return summary


# --
# get_volume_details()
# Returns details of volume utilization for a tenant
#
def get_volume_details(p_cinder_client):
    volumelist = p_cinder_client.volumes.list()
    total_provisioned = 0

    for volumes in volumelist:
        total_provisioned = total_provisioned + volumes.size

    summary = {}
    summary['total_vols_count'] = len(volumelist)
    summary['total_vols_provisioned_capacity'] = total_provisioned
    return summary


# --
# get_object_details()
# Returns details of object utilization for a tenant
#
def get_object_details(p_swift_client):
    summary = {}
    t_object_store = p_swift_client.get_account()

    summary['total_container_count']     = int(t_object_store[0]['x-account-container-count'])
    summary['total_object_count']        = int(t_object_store[0]['x-account-object-count'])
    summary['total_object_storage_used'] = float("{0:.2f}".format(int(t_object_store[0]['x-account-bytes-used']) / (1024*1024*1024)))
    return summary


# --
# get_all_tenant_flavorcount()
# Returns dict of dict for all tenants
# This is of the form
#    d['Tenant_Name'] = {
#        "m1.tiny"       : int,
#        "m1.small"      : int,
#        "m1.medium"     : int,
#        "m1.large"      : int,
#        "m1.xlarge"     : int,
#        "m1.2xlarge"    : int,
#        "m1.4xlarge"    : int,
#        "m1.8xlarge"    : int,
#        "custom"        : int
#    }
#
def get_all_tenant_flavorcount():
    keystone = get_keystone_client()
    tenantlist = keystone.tenants.list()

    global _debug
    if _debug:
        print '[+] Crunching flavor stats for all tenants ...'

    d = {}

    for tenant in tenantlist:

        if tenant.enabled == False:
            t_tenant_name = tenant.name

            d[t_tenant_name] = {
                'm1.tiny'   : 'disabled',
                'm1.small'  : 'disabled',
                'm1.medium' : 'disabled',
                'm1.large'  : 'disabled',
                'm1.xlarge' : 'disabled',
                'm1.2xlarge': 'disabled',
                'm1.4xlarge': 'disabled',
                'm1.8xlarge': 'disabled',
                'custom'    : 'disabled',
            }

        else:
            nova = get_nova_client(tenant.name)
            t_tenant_name  = tenant.name
            t_flavor_details = get_flavor_count(nova)

            d[t_tenant_name] = {
                'm1.tiny'   : t_flavor_details['m1.tiny'],
                'm1.small'  : t_flavor_details['m1.small'],
                'm1.medium' : t_flavor_details['m1.medium'],
                'm1.large'  : t_flavor_details['m1.large'],
                'm1.xlarge' : t_flavor_details['m1.xlarge'],
                'm1.2xlarge': t_flavor_details['m1.2xlarge'],
                'm1.4xlarge': t_flavor_details['m1.4xlarge'],
                'm1.8xlarge': t_flavor_details['m1.8xlarge'],
                'custom'    : t_flavor_details['custom']
            }

        if _debug == True:
            print "    [-] %s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (t_tenant_name,
                    t_flavor_details['m1.tiny'],
                    t_flavor_details['m1.small'],
                    t_flavor_details['m1.medium'],
                    t_flavor_details['m1.large'],
                    t_flavor_details['m1.xlarge'],
                    t_flavor_details['m1.2xlarge'],
                    t_flavor_details['m1.4xlarge'],
                    t_flavor_details['m1.8xlarge'],
                    t_flavor_details['custom'] )

    return d


# --
# get_all_tenant_utilization()
# Returns a (k,v) dict where k = tenantname and v is dict of pulled values
#
def get_all_tenant_utilization():
    keystone = get_keystone_client()
    tenantlist = keystone.tenants.list()

    global _debug
    if _debug == True:
        print '[+] Crunching utilization stats for all tenants ...'

    aggr_inst_prov = 0
    aggr_inst_active = 0
    aggr_vcpu_prov = 0
    aggr_vcpu_active = 0
    aggr_ram_prov = 0
    aggr_ram_active = 0
    aggr_disk_prov = 0
    aggr_floatip_alloc = 0
    aggr_floatip_disassoc = 0
    aggr_persist_volcount       = 0
    aggr_persist_provisioned    = 0
    aggr_container_count    = 0
    aggr_object_count = 0
    aggr_object_storage_used = 0

    # Will be returning an aggregate at the end .. so lets use OrderedDict()
    d = collections.OrderedDict()

    for tenant in tenantlist:

        # Skip disabled tenants
        if tenant.enabled == False:
            t_tenant_name           = tenant.name
            t_instances             = 'disabled'
            t_instances_active      = 'disabled'
            t_vcpu                  = 'disabled'
            t_vcpu_active           = 'disabled'
            t_ram                   = 'disabled'
            t_ram_active            = 'disabled'
            t_disk_ephemeral        = 'disabled'
            t_float_allocated       = 'disabled'
            t_float_disassociated   = 'disabled'
            t_persist_volcount      = 'disabled'
            t_persist_provisioned   = 'disabled'
            t_container_count       = 'disabled'
            t_object_count          = 'disabled'
            t_object_storage_used   = 'disabled'

        else :
            nova = get_nova_client(tenant.name)
            cinder = get_cinder_client(tenant.name)
            swift = get_swift_client(tenant.name)

            compute_summary = get_instance_details(nova)
            storage_summary = get_volume_details(cinder)
            object_summary  = get_object_details(swift)

            t_tenant_name           = tenant.name
            t_instances             = compute_summary['total_instances']
            t_instances_active      = compute_summary['total_instances_active']
            t_vcpu                  = compute_summary['total_vcpu']
            t_vcpu_active           = compute_summary['total_vcpu_active']
            t_ram                   = compute_summary['total_ram'] / 1024
            t_ram_active            = compute_summary['total_ram_active'] / 1024
            t_disk_ephemeral        = compute_summary['total_disk'] + compute_summary['total_ephemeral']
            t_float_allocated       = compute_summary['total_floatingip_allocated']
            t_float_disassociated   = compute_summary['total_floatingip_disassocated']
            t_persist_volcount      = storage_summary['total_vols_count']
            t_persist_provisioned   = storage_summary['total_vols_provisioned_capacity']
            t_container_count       = object_summary['total_container_count']
            t_object_count          = object_summary['total_object_count']
            t_object_storage_used   = object_summary['total_object_storage_used']

            aggr_inst_prov              = aggr_inst_prov + t_instances
            aggr_inst_active            = aggr_inst_active + t_instances_active
            aggr_vcpu_prov              = aggr_vcpu_prov + t_vcpu
            aggr_vcpu_active            = aggr_vcpu_active + t_vcpu_active
            aggr_ram_prov               = aggr_ram_prov + t_ram
            aggr_ram_active             = aggr_ram_active + t_ram_active
            aggr_disk_prov              = aggr_disk_prov + t_disk_ephemeral
            aggr_floatip_alloc          = aggr_floatip_alloc + t_float_allocated
            aggr_floatip_disassoc       = aggr_floatip_disassoc + t_float_disassociated
            aggr_persist_volcount       = aggr_persist_volcount + t_persist_volcount
            aggr_persist_provisioned    = aggr_persist_provisioned + t_persist_provisioned
            aggr_container_count        = aggr_container_count + t_container_count
            aggr_object_count           = aggr_object_count + t_object_count
            aggr_object_storage_used    = aggr_object_storage_used + t_object_storage_used

        # Inst_Prov,Inst_Active,VCPU_Prov,VCPU_Active,RAM_Prov,RAM_Active,Disk_Prov_GB,FloatIP_Alloc,FloatIP_Disassoc,Vols_Prov,Vols_Prov_GB,Object_Containers,Object_Count,Object_Storage_Used_GB"
        # k,v where k becomes header
        d[t_tenant_name] = {
            'Inst_Prov'         : t_instances,
            'Inst_Active'       : t_instances_active,
            'VCPU_Prov'         : t_vcpu,
            'VCPU_Active'       : t_vcpu_active,
            'RAM_Prov'          : t_ram,
            'RAM_Active'        : t_ram_active,
            'Disk_Prov_GB'      : t_disk_ephemeral,
            'FloatIP_Alloc'     : t_float_allocated,
            'FloatIP_Disassoc'  : t_float_disassociated,
            'Vols_Prov'         : t_persist_volcount,
            'Vols_Prov_GB'      : t_persist_provisioned,
            'Object_Containers' : t_container_count,
            'Object_Count'      : t_object_count,
            'Object_Storage_Used_GB' : t_object_storage_used
        }

        if _debug == True:
            print "    [-] %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s" % (
                    t_tenant_name,
                    t_instances,
                    t_instances_active,
                    t_vcpu,
                    t_vcpu_active,
                    t_ram,
                    t_ram_active,
                    t_disk_ephemeral,
                    t_float_allocated,
                    t_float_disassociated,
                    t_persist_volcount,
                    t_persist_provisioned,
                    t_container_count,
                    t_object_count,
                    t_object_storage_used)

    # Print Aggregates
    if _debug == True:
        print "    [-] Total,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                aggr_inst_prov,
                aggr_inst_active,
                aggr_vcpu_prov,
                aggr_vcpu_active,
                aggr_ram_prov,
                aggr_ram_active,
                aggr_disk_prov,
                aggr_floatip_alloc,
                aggr_floatip_disassoc,
                aggr_persist_volcount,
                aggr_persist_provisioned,
                aggr_container_count,
                aggr_object_count,
                aggr_object_storage_used)

    # Adding aggregates at the end of ordered dict
    d['_Total'] = {
            'Inst_Prov'         : aggr_inst_prov,
            'Inst_Active'       : aggr_inst_active,
            'VCPU_Prov'         : aggr_vcpu_prov,
            'VCPU_Active'       : aggr_vcpu_active,
            'RAM_Prov'          : aggr_ram_prov,
            'RAM_Active'        : aggr_ram_active,
            'Disk_Prov_GB'      : aggr_disk_prov,
            'FloatIP_Alloc'     : aggr_floatip_alloc,
            'FloatIP_Disassoc'  : aggr_floatip_disassoc,
            'Vols_Prov'         : aggr_persist_volcount,
            'Vols_Prov_GB'      : aggr_persist_provisioned,
            'Object_Containers' : aggr_container_count,
            'Object_Count'      : aggr_object_count,
            'Object_Storage_Used_GB' : aggr_object_storage_used
    }

    return d


# --
# csv_report()
# Write out the csv formated dict values
#     [d_report]  single level ordered dict that is to be rendered as a table
#     [l_header]  table headers that double up as keys to the d_report dict
#     [file_name] the file that the final csv is to be written into
#
# Note : d_report must be ordered dict for aggregates to be printed last
def csv_report(d_report,l_header,file_name):
    global _debug
    if _debug == True:
        print "[+] Formating report as CSV .."
        print d_report
        print l_header

    # If file not writable then console
    file_handle = open(file_name,'w') if file_name else sys.stdout

    csv_writer = csv.writer(file_handle)

    # Construct headers to be written to csv first
    # first element intentionally left blank for this function to be generic
    t_tenant_header = []
    t_tenant_header.append("")

    for header in l_header:
        t_tenant_header.append(header)

    csv_writer.writerow(t_tenant_header)

    # Construct each tenant row as a list so that it can be consumed by pycsv
    for k in d_report:
        t_tenant_name = k
        t_tenant_values = d_report[k]

        t_tenant_row = []
        t_tenant_row.append(t_tenant_name)
        for header in l_header:
            t_tenant_row.append(t_tenant_values[header])

        csv_writer.writerow(t_tenant_row)


def main():
    parser = argparse.ArgumentParser(description="Command-line interface for generating reports for Openstack clusters")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--flavorcount', help='Per tenant flavorcount',
                       action="store_true", default=False)
    group.add_argument('-u', '--utilization', help='Per tenant utilization',
                       action="store_true", default=False)

    parser.add_argument('-o', '--output', help='Destination file to store result')
    parser.add_argument('-d', '--debug', help='Enable Debug',action="store_true")
    parser.add_argument('--version', action='version', version='1.0')

    cli_opts = parser.parse_args()

    output_file = cli_opts.output

    if cli_opts.debug == True:
        global _debug
        _debug = True
        print "[+] %s" % cli_opts

    if cli_opts.flavorcount == True:
        # Compute dict of tenantwise flavorcount for all tenants
        report = get_all_tenant_flavorcount()

        # Prepare report header
        report_headers = []
        for flavors in flavorListDefault:
            report_headers.append(flavors)
        report_headers.append("custom")

        # Write the report alongwith header to target
        csv_report(report,report_headers,output_file)
        return

    if cli_opts.utilization == True:
        # Compute tenantwise utilization for all tenants
        report = get_all_tenant_utilization()

        # Prepare report header
        report_headers = [
            'Inst_Prov',
            'Inst_Active',
            'VCPU_Prov',
            'VCPU_Active',
            'RAM_Prov',
            'RAM_Active',
            'Disk_Prov_GB',
            'FloatIP_Alloc',
            'FloatIP_Disassoc',
            'Vols_Prov',
            'Vols_Prov_GB',
            'Object_Containers',
            'Object_Count',
            'Object_Storage_Used_GB'
        ]
        # Write header + report to target
        csv_report(report,report_headers,output_file)


if __name__ == "__main__":
    main()
