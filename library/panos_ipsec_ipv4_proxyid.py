#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

#  Copyright 2019 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: panos_ipsec_ipv4_proxyid
short_description: Configures IPv4 Proxy Id on an IPSec Tunnel
author: "Heiko Burghardt (@odysseus107)"
version_added: "2.8"
requirements:
    - pan-python can be obtained from PyPI U(https://pypi.python.org/pypi/pan-python)
    - pandevice can be obtained from PyPI U(https://pypi.python.org/pypi/pandevice)
notes:
    - Panorama is supported.
    - Check mode is supported.
extends_documentation_fragment:
    - panos.transitional_provider
    - panos.state
    - panos.full_template_support
options:
    name:
        description:
            - The Proxy ID
        required: true
    tunnel_name:
        description:
            - Tunnel Name
        required: true
    local:
        description:
            - IP subnet or IP address represents local network
        required: true
    remote:
        description:
            - IP subnet or IP address represents remote network
        required: true
    any_protocol:
        description:
            - Any protocol boolean, default: True
    number_proto:
        description:
            - Numbered Protocol: protocol number (1-254)
    tcp_local_port:
        description:
            - Protocol TCP: local port
    tcp_remote_port:
        description:
            - Protocol TCP: remote port
    udp_local_port:
        description:
            Protocol UDP: local port
    udp_remote_port:
        description:
            - Protocol UDP: remote port
    commit:
        description:
            - Commit configuration if changed.
        default: True
'''

EXAMPLES = '''
- name: Add IPSec IPv4 Proxy ID
  panos_ipsec_ipv4_proxyid:
    provider: '{{ provider }}'
    name: 'IPSec-ProxyId'
    tunnel_name: 'Default_Tunnel'
    local: '192.168.2.0/24'
    remote: '192.168.1.0/24'
    commit: False
'''

RETURN = '''
# Default return values
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.panos.panos import get_connection

try:
    from pandevice.network import IpsecTunnel
    from pandevice.network import IpsecTunnelIpv4ProxyId
    from pandevice.errors import PanDeviceError
except ImportError:
    pass


def main():
    helper = get_connection(
        template=True,
        template_stack=True,
        with_classic_provider_spec=True,
        with_state=True,
        argument_spec=dict(
            name=dict(required=True),
            tunnel_name=dict(default='default'),
            local=dict(default='192.168.2.0/24'),
            remote=dict(default='192.168.1.0/24'),
            any_protocol=dict(type='bool', default=True),
            number_proto=dict(),
            tcp_local_port=dict(),
            tcp_remote_port=dict(),
            udp_local_port=dict(),
            udp_remote_port=dict(),
            commit=dict(type='bool', default=True),
        )
    )

    module = AnsibleModule(
        argument_spec=helper.argument_spec,
        supports_check_mode=True,
        required_one_of=helper.required_one_of
    )

    # Object specifications
    spec = {
        'name': module.params['name'],
        'local': module.params['local'],
        'remote': module.params['remote'],
        'any_protocol': module.params['any_protocol'],
        'number_protocol': module.params['number_proto'],
        'tcp_local_port': module.params['tcp_local_port'],
        'tcp_remote_port': module.params['tcp_remote_port'],
        'udp_local_port': module.params['udp_local_port'],
        'udp_remote_port': module.params['udp_remote_port'],
    }

    # Additional infos
    commit = module.params['commit']

    # Verify libs are present, get parent object.
    parent = helper.get_pandevice_parent(module)
    tunnel_name = module.params['tunnel_name']

    # Retrieve list of tunnel objects
    try:
        tunnel_list = IpsecTunnel.refreshall(parent, add=False)
    except PanDeviceError as e:
        module.fail_json(msg='Failed refresh: {0}'.format(e))

    # get the specific tunnel object named by tunnel_name
    for tunnel in tunnel_list:
        if tunnel.name == tunnel_name:
            parent.add(tunnel)
            break
    else:
        module.fail_json(msg='Tunnel named "{0}" does not exist'.format(tunnel_name))

    # get the listing
    try:
        listing = IpsecTunnelIpv4ProxyId.refreshall(tunnel, add=False)
    except PanDeviceError as e:
        module.fail_json(msg='Failed refresh: {0}'.format(e))

    obj = IpsecTunnelIpv4ProxyId(**spec)
    tunnel.add(obj)

    # Apply the state.
    changed = helper.apply_state(obj, listing, module)

    # Commit.
    if commit and changed:
        helper.commit(module)

    # Done.
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()