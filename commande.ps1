#Récupérer les utilisateurs du domaine
    resultat = t.execute(
        'powershell -NoProfile -Command "[Console]::OutputEncoding = '
        '[System.Text.Encoding]::UTF8; '
        'Import-Module ActiveDirectory; '
        'Get-ADUser -Filter * -Properties SamAccountName, DisplayName | '
        'Select SamAccountName, DisplayName | ConvertTo-Csv -NoTypeInformation"'
    )
#Récupérer les groupes du domaine
Get-ADGroup -Filter * -Properties SamAccountName |
    Select SamAccountName |
    ConvertTo-Csv -NoTypeInformation


#Récupérer les machines du domaine
Get-ADComputer -Filter * -Properties Name, IPv4Address |
    Select Name, IPv4Address |
    ConvertTo-Csv -NoTypeInformation


# Récupérer les comptes ad expiré
Import-Module ActiveDirectory
Search-ADAccount -AccountExpired -UsersOnly |
  Format-Table Name, SamAccountName, UserPrincipalName, Enabled, LastLogonDate -AutoSize

    
#lister les contrôleurs de domaine et leurs rôles FSMO
Get-ADDomainController -Filter * |
  Select @{n='DC';e={$_.HostName}}, Site, IPv4Address, IsGlobalCatalog,
         @{n='SchemaMaster';e={ $_.HostName -ieq (Get-ADForest).SchemaMaster }},
         @{n='DomainNamingMaster';e={ $_.HostName -ieq (Get-ADForest).DomainNamingMaster }},
         @{n='PDCEmulator';e={ $_.HostName -ieq (Get-ADDomain).PDCEmulator }},
         @{n='RIDMaster';e={ $_.HostName -ieq (Get-ADDomain).RIDMaster }},
         @{n='InfrastructureMaster';e={ $_.HostName -ieq (Get-ADDomain).InfrastructureMaster }} |
  ConvertTo-Csv -NoTypeInformation