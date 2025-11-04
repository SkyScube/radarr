import csv
from io import StringIO

from classe import ssh

class commande:
    def __init__(self):
        pass

    @staticmethod
    def user_domain(t):
        command = (
            'powershell -NoProfile -Command "'
            '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            'Import-Module ActiveDirectory; '
            'Get-ADUser -Filter * -Properties '
            'SamAccountName, DisplayName, Enabled, LockedOut, AccountExpirationDate, '
            'PasswordLastSet, PasswordNeverExpires, UserPrincipalName | '
            'Select SamAccountName, DisplayName, UserPrincipalName, Enabled, LockedOut, '
            'PasswordNeverExpires, PasswordLastSet, AccountExpirationDate, '
            '@{Name=\'IsExpired\';Expression={($_.AccountExpirationDate -ne $null) -and '
            '($_.AccountExpirationDate -lt (Get-Date))}} | '
            'ConvertTo-Csv -NoTypeInformation"'
        )
        brut = t.execute(command)
        flux_csv = StringIO(brut)
        lecteur = csv.DictReader(flux_csv)
        for ligne in lecteur:
            if not ligne:
                continue
            sam = ligne.get('SamAccountName', '').strip()
            display = ligne.get('DisplayName', '').strip()
            principal = ligne.get('UserPrincipalName', '').strip()
            enabled = ligne.get('Enabled', '').strip()
            locked = ligne.get('LockedOut', '').strip()
            never_exp = ligne.get('PasswordNeverExpires', '').strip()
            pwd_last = ligne.get('PasswordLastSet', '').strip()
            expiration = ligne.get('AccountExpirationDate', '').strip()
            is_expired = ligne.get('IsExpired', '').strip()
            if sam or display:
                print(
                    f"{sam} ({display})\n"
                    f"  UPN : {principal}\n"
                    f"  Enabled : {enabled} | Locked : {locked}\n"
                    f"  Password never expires : {never_exp} | Last set : {pwd_last}\n"
                    f"  Expiration : {expiration} | Is expired : {is_expired}\n"
                )

    @staticmethod
    def group_user_domain(t):
        command = (
            'powershell -NoProfile -Command "'
            '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            'Import-Module ActiveDirectory; '
            'Get-ADGroup -Filter * -Properties SamAccountName | '
            'Select SamAccountName | ConvertTo-Csv -NoTypeInformation"'
        )
        resultat = t.execute(command)
        flux_csv = StringIO(resultat)
        lecteur = csv.DictReader(flux_csv)
        for ligne in lecteur:
            if not ligne:
                continue
            sam = ligne.get('SamAccountName', '').strip()
            if sam:
                print(f"{sam}")

    @staticmethod
    def computers_domain(t):
        command = (
            'powershell -NoProfile -Command "'
            '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            'Import-Module ActiveDirectory; '
            'Get-ADComputer -Filter * -Properties Name, IPv4Address | '
            'Select Name, IPv4Address | ConvertTo-Csv -NoTypeInformation"'
        )
        raw_csv = t.execute(command)
        for row in csv.DictReader(StringIO(raw_csv)):
            name = row.get('Name', '').strip()
            ipv4 = row.get('IPv4Address', '').strip()
            if name or ipv4:
                print(f"{name} -> {ipv4}")

    @staticmethod            
    def domain_controllers(t):
        command = (
            'powershell -NoProfile -Command "'
            '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            'Import-Module ActiveDirectory; '
            'Get-ADDomainController -Filter * | '
            'Select @{n=\'DC\';e={$_.HostName}}, Site, IPv4Address, IsGlobalCatalog, '
            '@{n=\'SchemaMaster\';e={ $_.HostName -ieq (Get-ADForest).SchemaMaster }}, '
            '@{n=\'DomainNamingMaster\';e={ $_.HostName -ieq (Get-ADForest).DomainNamingMaster }}, '
            '@{n=\'PDCEmulator\';e={ $_.HostName -ieq (Get-ADDomain).PDCEmulator }}, '
            '@{n=\'RIDMaster\';e={ $_.HostName -ieq (Get-ADDomain).RIDMaster }}, '
            '@{n=\'InfrastructureMaster\';e={ $_.HostName -ieq (Get-ADDomain).InfrastructureMaster }} | '
            'ConvertTo-Csv -NoTypeInformation"'
        )
        raw_csv = t.execute(command)
        for row in csv.DictReader(StringIO(raw_csv)):
            if not row:
                continue
            print(
                f"{row.get('DC', '').strip()} | Site={row.get('Site', '').strip()} | "
                f"IPv4={row.get('IPv4Address', '').strip()} | GC={row.get('IsGlobalCatalog', '').strip()} | "
                f"Schema={row.get('SchemaMaster', '').strip()} | DomainNaming={row.get('DomainNamingMaster', '').strip()} | "
                f"PDC={row.get('PDCEmulator', '').strip()} | RID={row.get('RIDMaster', '').strip()} | "
                f"Infra={row.get('InfrastructureMaster', '').strip()}"
            )


if __name__ == "__main__":
    hostname = "192.168.151.39"
    username = "Administrateur"
    password = "AdminP4ss"
    t = ssh(hostname, username, password)
    command = commande()
    t.connect()
    command.domain_controllers(t)
    t.close_connection()

