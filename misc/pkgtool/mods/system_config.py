from mods.utils import EmptyObject
from mods.utils import Utils
from res.etc_network import EtcNetwork 
from res.etc_config import EtcConfig


def todo_set_ip_or_dhcp(name, is_dhcp, addr=None, gw=None, dns=None, domains=None):
    if not name:
        return False
    if not is_dhcp and not (addr and gw and dns and domains):
        return False
    eth = EmptyObject()
    eth.name = name
    if not is_dhcp:
        eth.address = addr
        eth.gateway = gw
        eth.dns = dns
        eth.domains = domains
        data = EtcNetwork.systemd_eth_static.format(eth=eth)
    else:
        data = EtcNetwork.systemd_eth_dhcp.format(eth=eth)

    start = 10
    fpath = None
    netd = "/etc/systemd/network"
    netf = "%s-eth-dhcp.network" if is_dhcp else "%s-eth-static.network"
    while start < 90:
        fpath = Path(netd).joinpath(netf % start)
        if not fpath.exists(): break
        start += 5
        fpath = None
    if not fpath: return False
    fpath.write_text(data)
    return fpath.exists()

def todo_set_resolv_conf(domain, nameserver0, nameserver1):
    fpath = Path("/etc/resolv.conf")
    if fpath.exists(): return False
    if not domain or not nameserver0: return False
    if not nameserver1: nameserver0 = nameserver1
    resolv = EmptyObject()
    resolv.domain = domain
    resolv.nameserver0 = nameserver0
    resolv.nameserver1 = nameserver1
    data = EtcNetwork.resolv_conf.format(resolv=resolv)
    fpath.write_text(data)
    return fpath.exists()

def todo_set_hostname(hostname):
    fpath = Path("/etc/hostname")
    if fpath.exists(): return False
    fpath.write_text(hostname)
    return fpath.exists()

def todo_set_hosts(ip, FQDN, alias_list=[]):
    fpath = Path("/etc/hosts")
    if fpath.exists(): return False
    if not ip or not FQDN: return False
    host = EmptyObject()
    host.ip = ip
    host.FQDN = FQDN
    host.alias_list = alias_list
    data = EtcNetwork.hosts.format(host=host)
    fpath.write_text(data)
    return fpath.exists()

def todo_set_adjtime():
    fpath = Path("/etc/adjtime")
    if fpath.exists(): return False
    fpath.write_text(EtcConfig.adjtime)
    return fpath.exists()

def todo_set_inputrc():
    fpath = Path("/etc/inputrc")
    if fpath.exists(): return False
    fpath.write_text(EtcConfig.inputrc)
    return fpath.exists()

def todo_set_shells():
    fpath = Path("/etc/shells")
    if fpath.exists(): return False
    fpath.write_text(EtcConfig.shells)
    return fpath.exists()
