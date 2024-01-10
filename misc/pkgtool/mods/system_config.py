from res.etc_config import etc_adjtime
from res.etc_config import etc_inputrc
from res.etc_config import etc_shells
from mods.utils import Utils


def todo_set_ip_or_dhcp(name, is_dhcp, addr=None, gw=None, dns=None, domains=None):
    if not name:
        return False
    if not is_dhcp and not (addr and gw and dns and domains):
        return False
    start = 10
    netp = None
    netd = "/etc/systemd/network"
    netf = "%s-eth-dhcp.network" if is_dhcp else "%s-eth-static.network"
    while start < 90:
        netp = Path(netd).joinpath(netf % start)
        if not netp.exists(): break
        start += 5
        netp = None
    if not netp:
        return False
    lines = []
    lines.append("[Match]\nName=%s" % name)
    lines.append("")
    if not is_dhcp:
        lines.append("[Network]\nAddress=%s\nGateway=%s\nDNS=%s\nDomains=%s" % (addr, gw, dns, domains))
    else:
        lines.append("[Network]\nDHCP=ipv4")
        lines.append("[DHCPv4]\nUseDomains=true")
    return Utils.write_lines(netp, lines)

def todo_set_hosts(ADDR, FQDN, HOSTNAME, alias=[]):
    hostsp = Path("/etc/hosts")
    if hostsp.exists():
        return False
    lines = []
    lines.append("# Begin /etc/hosts")
    lines.append("")
    lines.append("127.0.0.1 localhost.localdomain localhost")
    #127.0.1.1 <FQDN> <HOSTNAME>
    if FQDN and HOSTNAME:
        lines.append("127.0.1.1 %s %s" % (FQDN, HOSTNAME))
    #<192.168.0.2> <FQDN> <HOSTNAME> [alias1] [alias2] ...
    if ADDR and FQDN and HOSTNAME:
        parts = [ADDR, FQDN, HOSTNAME]
        parts.extend(alias)
        lines.append(" ".join(parts))
    lines.append("::1       localhost ip6-localhost ip6-loopback")
    lines.append("ff02::1   ip6-allnodes")
    lines.append("ff02::2   ip6-allrouters")
    lines.append("")
    lines.append("# End /etc/hosts")
    return Utils.write_lines(hostsp, lines)

def todo_set_adjtime():
    fpath = Path("/etc/adjtime")
    if fpath.exists(): return False
    if etc_adjtime: fpath.write_text(etc_adjtime)

def todo_set_inputrc():
    fpath = Path("/etc/inputrc")
    if fpath.exists(): return False
    if etc_inputrc: fpath.write_text(etc_inputrc)

def todo_set_shells():
    fpath = Path("/etc/shells")
    if fpath.exists(): return False
    if etc_shells: fpath.write_text(etc_shells)
