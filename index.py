import csv
from io import StringIO
from typing import Dict, List

from classe import ssh


class commande:
    """Ensemble de commandes distantes pour interroger Active Directory."""

    def __init__(self):
        """Initialise un conteneur de commandes."""
        pass

    @staticmethod
    def user_domain(t) -> List[Dict[str, str]]:
        """Récupère les utilisateurs du domaine et retourne la liste des enregistrements."""
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
        lignes: List[Dict[str, str]] = []
        for ligne in lecteur:
            if not ligne:
                continue
            record = {
                'SamAccountName': ligne.get('SamAccountName', '').strip(),
                'DisplayName': ligne.get('DisplayName', '').strip(),
                'UserPrincipalName': ligne.get('UserPrincipalName', '').strip(),
                'Enabled': ligne.get('Enabled', '').strip(),
                'LockedOut': ligne.get('LockedOut', '').strip(),
                'PasswordNeverExpires': ligne.get('PasswordNeverExpires', '').strip(),
                'PasswordLastSet': ligne.get('PasswordLastSet', '').strip(),
                'AccountExpirationDate': ligne.get('AccountExpirationDate', '').strip(),
                'IsExpired': ligne.get('IsExpired', '').strip(),
            }
            lignes.append(record)
            if record['SamAccountName'] or record['DisplayName']:
                print(
                    f"{record['SamAccountName']} ({record['DisplayName']})\n"
                    f"  UPN : {record['UserPrincipalName']}\n"
                    f"  Enabled : {record['Enabled']} | Locked : {record['LockedOut']}\n"
                    f"  Password never expires : {record['PasswordNeverExpires']} | Last set : {record['PasswordLastSet']}\n"
                    f"  Expiration : {record['AccountExpirationDate']} | Is expired : {record['IsExpired']}\n"
                )
        return lignes

    @staticmethod
    def group_user_domain(t) -> List[Dict[str, str]]:
        """Liste les groupes AD et retourne les SamAccountName disponibles."""
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
        lignes: List[Dict[str, str]] = []
        for ligne in lecteur:
            if not ligne:
                continue
            sam = ligne.get('SamAccountName', '').strip()
            if sam:
                lignes.append({'SamAccountName': sam})
                print(sam)
        return lignes

    @staticmethod
    def computers_domain(t) -> List[Dict[str, str]]:
        """Renvoie l'inventaire des postes/machines du domaine avec leur IP."""
        command = (
            'powershell -NoProfile -Command "'
            '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            'Import-Module ActiveDirectory; '
            'Get-ADComputer -Filter * -Properties Name, IPv4Address | '
            'Select Name, IPv4Address | ConvertTo-Csv -NoTypeInformation"'
        )
        raw_csv = t.execute(command)
        lignes: List[Dict[str, str]] = []
        for row in csv.DictReader(StringIO(raw_csv)):
            if not row:
                continue
            record = {
                'Name': row.get('Name', '').strip(),
                'IPv4Address': row.get('IPv4Address', '').strip(),
            }
            if record['Name'] or record['IPv4Address']:
                lignes.append(record)
                print(f"{record['Name']} -> {record['IPv4Address']}")
        return lignes

    @staticmethod
    def domain_controllers(t) -> List[Dict[str, str]]:
        """Liste les contrôleurs de domaine et leurs rôles FSMO."""
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
        lignes: List[Dict[str, str]] = []
        for row in csv.DictReader(StringIO(raw_csv)):
            if not row:
                continue
            record = {
                'DC': row.get('DC', '').strip(),
                'Site': row.get('Site', '').strip(),
                'IPv4Address': row.get('IPv4Address', '').strip(),
                'IsGlobalCatalog': row.get('IsGlobalCatalog', '').strip(),
                'SchemaMaster': row.get('SchemaMaster', '').strip(),
                'DomainNamingMaster': row.get('DomainNamingMaster', '').strip(),
                'PDCEmulator': row.get('PDCEmulator', '').strip(),
                'RIDMaster': row.get('RIDMaster', '').strip(),
                'InfrastructureMaster': row.get('InfrastructureMaster', '').strip(),
            }
            lignes.append(record)
            print(
                f"{record['DC']} | Site={record['Site']} | "
                f"IPv4={record['IPv4Address']} | GC={record['IsGlobalCatalog']} | "
                f"Schema={record['SchemaMaster']} | DomainNaming={record['DomainNamingMaster']} | "
                f"PDC={record['PDCEmulator']} | RID={record['RIDMaster']} | "
                f"Infra={record['InfrastructureMaster']}"
            )
        return lignes


if __name__ == "__main__":
    hostname = "192.168.151.39"
    username = "Administrateur"
    password = "AdminP4ss"
    t = ssh(hostname, username, password)
    command = commande()
    t.connect()
    command.user_domain(t)
    command.group_user_domain(t)
    command.computers_domain(t)
    command.domain_controllers(t)
    t.close_connection()
