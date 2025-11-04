import csv
from io import StringIO
from typing import List, Dict

from commands import PowerShellCommand


class GetADUsersCommand(PowerShellCommand):
    def __init__(self):
        super().__init__(
            command=(
                "Get-ADUser -Filter * -Properties SamAccountName, DisplayName | "
                "Select SamAccountName, DisplayName | ConvertTo-Csv -NoTypeInformation"
            ),
            modules=["ActiveDirectory"],
        )

    def parse(self, raw_output: str) -> List[Dict[str, str]]:
        reader = csv.DictReader(StringIO(raw_output))
        return [
            {key: (value or '').strip() for key, value in row.items() if key}
            for row in reader
            if row
        ]
