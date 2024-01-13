

network_help = """\
> If you will not use systemd-networkd for network configuration
> disable a service to prevent an error message during boot:
    systemctl disable systemd-networkd-wait-online

> If you prefer to use the classic or customized network interface names, there are three alternative ways to do that:
>> a). Mask udev's .link file for the default policy:
    ln -s /dev/null /etc/systemd/network/99-default.link
>> b). Create a manual naming schemem, to create .link files in /etc/systemd/network/ that 
>>    select an explicit name or a better naming scheme for your network interfaces.
>>    See systemd.link(5) for more information.
    cat > /etc/systemd/network/10-ether0.link << "EOF"
    [Match]
    # Change the MAC address as appropriate for your network device
    MACAddress=12:34:45:78:90:AB

    [Link]
    Name=ether0
    EOF
>> c). In /boot/grub/grub.cfg, pass the option net.ifnames=0 on the kernel command line.

> If using methods incompatible with systemd-resolved to configure your network interfaces (ex: ppp, etc.),
> or if using any type of local resolver (ex: bind, dnsmasq, unbound, etc.)
> or any other software that generates an /etc/resolv.conf
> the systemd-resolved service should not be used.
    systemctl disable systemd-resolved


"""

#e.g /etc/systemd/network/10-eth-static.network
etc_systemd_network_eth_static = """#zen-etc template
[Match]
Name={eth.name} #<network-device-name>

[Network]
Address={eth.address}   #192.168.0.2/24
Gateway={eth.gateway}   #192.168.0.1
DNS={eth.dns}           #192.168.0.1
Domains={eth.domains}   #<Your Domain Name>
"""

#e.g /etc/systemd/network/10-eth-dhcp.network
etc_systemd_network_eth_dhcp = """#zen-etc template
[Match]
Name={eth.name} #<network-device-name>

[Network]
DHCP=ipv4

[DHCPv4]
UseDomains=true
"""

etc_resolv_conf = """#zen-etc template
# Begin /etc/resolv.conf

domain {resolv.domain} #<Your Domain Name>
nameserver {resolv.nameserver0} #<IP address of your primary nameserver>
nameserver {resolv.nameserver1} #<IP address of your secondary nameserver>

# End /etc/resolv.conf
"""

etc_hosts = """#zen-etc template
# Begin /etc/hosts

#outdated-format???
#127.0.0.1 localhost.localdomain localhost
#127.0.1.1 <FQDN> <HOSTNAME>

#<192.168.0.2> <FQDN> [alias1] [alias2] ...
{host.ip} {host.FQDN} {host.alias_list}
::1       ip6-localhost ip6-loopback
ff02::1   ip6-allnodes
ff02::2   ip6-allrouters

# End /etc/hosts
"""


class EtcNetwork(object):
    introduction = network_help
    systemd_eth_static = etc_systemd_network_eth_static
    systemd_eth_dhcp = etc_systemd_network_eth_dhcp
    resolv_conf = etc_resolv_conf
    hosts = etc_hosts

    def __init__(self):
        raise RuntimeError('Should not use object')

