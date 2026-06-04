# Enables -WhatIf and -Confirm support for this script.
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    # Optional domain name, such as domain.com.
    [string]$DomainName,

    # Optional switch to replace email addresses that already exist.
    [switch]$OverwriteExistingEmail
)

# Loads the Active Directory PowerShell commands.
Import-Module ActiveDirectory -ErrorAction Stop

# Ask for the domain name if it was not provided as a parameter.
if ([string]::IsNullOrWhiteSpace($DomainName)) {
    # Prompt for the email domain to use.
    $DomainName = Read-Host "Enter the email domain to append, for example domain.com"
}

# Remove spaces and a leading @ if one was entered.
$DomainName = $DomainName.Trim().TrimStart("@")

# Make sure the domain looks like a real domain name.
if ($DomainName -notmatch "^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$") {
    # Stop the script if the domain is not valid.
    throw "Domain name '$DomainName' does not look valid. Enter a value like domain.com."
}

# Get all AD users and include the mail and username fields.
$users = Get-ADUser -Filter * -Properties mail, SamAccountName

# Go through each user one at a time.
foreach ($user in $users) {
    # Skip users that do not have a username.
    if ([string]::IsNullOrWhiteSpace($user.SamAccountName)) {
        # Show which user was skipped and why.
        Write-Warning "Skipping '$($user.DistinguishedName)' because it does not have a SamAccountName."
        continue
    }

    # Skip users that already have email unless overwrite was requested.
    if ($user.mail -and -not $OverwriteExistingEmail) {
        # Show the existing email address.
        Write-Host "Skipping $($user.SamAccountName): mail is already set to $($user.mail)"
        continue
    }

    # Build the email address from username plus domain.
    $emailAddress = "$($user.SamAccountName)@$DomainName".ToLowerInvariant()

    # Respect -WhatIf and -Confirm before making the AD change.
    if ($PSCmdlet.ShouldProcess($user.SamAccountName, "Set mail attribute to $emailAddress")) {
        # Update the user's email address in Active Directory.
        Set-ADUser -Identity $user.DistinguishedName -EmailAddress $emailAddress
        # Show the updated user and email address.
        Write-Host "Updated $($user.SamAccountName): $emailAddress"
    }
}
