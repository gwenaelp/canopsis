# --------------------------------
# Copyright (c) 2011 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

# ---------------------------help----------------------
# Impossible de charger le fichier D:\Users\vcandeau\Desktop\send_events.ps1, car l'exécution de scripts est désactivée sur ce système. Pour plus d'informations, consultez « get-help about_signing ».
# PS C:\> Set-ExecutionPolicy RemoteSigned
# If not working use regedit and add 
# HKLM\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell\ExecutionPolicy (REG_SZ) : RemoteSigned
#------------------------------------------------------

#-----------------------------------Arg------------------------------
[CmdletBinding()]
Param(
      [string] $s,
      [string] $a,
      [string] $f,
      [string] $j,
      [int] $t,      
      [switch] $h,
      [switch] $d)      

#-----------------------------------System Lib------------------------------
[System.Reflection.Assembly]::LoadWithPartialName("System.Web") | out-null
Import-Module .\Newtonsoft.Json.dll

#-----------------------------------Variable------------------------------
$m_container  = New-Object System.Net.CookieContainer
$web = new-object net.webclient
$doc = new-object System.Xml.XmlDocument
$request_data = new-object System.Collections.Specialized.NameValueCollection 
$newtonsoft = new-object Newtonsoft.Json.Formatting
$authkey = $null
$server = 'localhost:8082'
$file_path = $null
$input_stream = $null
$json_string = $null
$event = $null
$timeout = 2000

#----------------------------------Function-----------------------------
function usage(){
	Write-Host(" Usage: send_event ")
	Write-Host
	Write-Host(" Options:")
	Write-Host("  -s [SERVER_ADDR]")
	Write-Host("	  webserver address (default : localhost:8082)")
	Write-Host("  -a [AUTHKEY]")
	Write-Host("  -f [FILE_PATH]")
	Write-Host("	 file contraining a json event to send")
	Write-Host("  -j [JSON]")  
	Write-Host("	 a json string containing a correct event to send")
	Write-Host("  -t ")
	Write-Host("	 Timeout in millisecond (default: 2000)")    
	Write-Host("  -d ")
	Write-Host("	 show debug")    
	Write-Host("  -h ")
	Write-Host("	 show help")
}

#---------------------------option processing----------------------
if ( $h -eq $true ) {
     usage
     exit 
}

if ( $t -ne $null ) {
     $timeout = $t
}

if ( $s -ne $null ) {
    $server = $s
}

if ( $a -ne $null ) {
    $authkey = $a
}

if ( $f -ne $null -and $f -ne ''  ) {
    if ( [IO.File]::Exists($f) ) {
        $file_path = $f
    } else {
        Write-Host('You must provide a valid path')
        exit
    }
} 

if ( $j -ne $null ) {  
    try{
        $doc = [System.Xml.XmlDocument][Newtonsoft.Json.JsonConvert]::DeserializeXmlNode( $j, 'json' )
        $json_string = $doc
    } catch {
        Write-Host('Bad json string' )
        if ( $d ) {
           Write-Host $_.Exception.ToString()
        }          
        exit 
    }   
}

#---------------------------authentificate-------------------------
if ( ! $authkey ) {
    Write-Host('You must provide a authkey to access to webserver')
    usage
    exit
}

### Set URI Var
$url_auth = "http://" + $server + "/autoLogin/" + $authkey
$url_me = $url = "http://" + $server + "/account/me"
$url_event = "http://" + $server + "/event/" 

### Getting Cookie & Test Authentification
try {
    $request = [System.Net.WebRequest]::Create($url_auth) 
    $request.CookieContainer = New-Object System.Net.CookieContainer
    $response = $request.GetResponse() 
    
    $web.Headers.add("Cookie", $response.Headers["Set-Cookie"])
    $r = $web.DownloadString( $url_me )
} catch {
    Write-Host( 'Error: bad response from server' )
    if ( $d ) {
        Write-Host $_.Exception.ToString()
    }      
    exit
}

### Converting JSON to XML
$doc = [System.Xml.XmlDocument][Newtonsoft.Json.JsonConvert]::DeserializeXmlNode( $r, 'json' )
if ( ! $doc.json.success ) {
    Write-Host('Bad authkey, no matching with any user')
	exit
}

#------------------------------find event source-----------------------
if ( $json_string -ne $null ) {
    $event = $json_string
}

if ( $file_path -ne $null ) {
    try{
        $content = Get-Content $file_path
        $content = $content -replace "None", "'None'"
        $content = $content -replace "''None''", "'None'"
        $doc = [System.Xml.XmlDocument][Newtonsoft.Json.JsonConvert]::DeserializeXmlNode( $content, 'json' )
        $event = $doc
    } catch {
        Write-Host('Bad json string')
        if ( $d ) {
           Write-Host $_.Exception.ToString()
        }  
        exit 
    } 
}

#-----------------------------prepare event-----------------------------
if ( $event -eq $null ) {
    Write-Host('Error: No json media found, you must provide file/command')
	exit
} 

#$event.Save( 'D:\Users\vcandeau\Desktop\canopsis_sendevent\test1.xml' )
if ( $event.json.perf_data_array ) {
    $json_perf_data_array = $null
    foreach( $perf_data_array in $event.json.perf_data_array  ) {
        if ( $json_perf_data_array -ne $null ) { $json_perf_data_array += "," }
        $str = [Newtonsoft.Json.JsonConvert]::SerializeXmlNode( $perf_data_array ) -replace '{"perf_data_array":{', "{" -replace '}}', '}'
        $json_perf_data_array += $str
        [Void]$event.json.RemoveChild($perf_data_array)
    }
    
    $json_perf_data_array = "[" + $json_perf_data_array + "]"
    $item = $event.CreateElement("perf_data_array")
    $item.PSBase.InnerText = $json_perf_data_array
    [void]$event.json.AppendChild($item)    
}

$item = $event.CreateElement("connector")
$item.PSBase.InnerText = "Cli"
[void]$event.json.AppendChild($item)

if ( ! $event.json.connector_name ) {
    $item = $event.CreateElement("connector_name")
    $item.PSBase.InnerText = "Send_win_event"
    [void]$event.json.AppendChild($item)
}

foreach( $node in $event.SelectNodes("/json/*")  ) {
   $request_data.Add( $node.LocalName, $node.InnerText ) 
}

#$event.Save( 'D:\Users\vcandeau\Desktop\canopsis_sendevent\test2.xml' )
#-----------------------------send event-----------------------------
try{
    $web.QueryString = $request_data
    $webpage = $web.UploadValues($url_event, "POST", $request_data) 
    $response = [System.Text.Encoding]::ASCII.GetString($webpage)  
    Write-Host $response
} catch {
    Write-Host( 'Error: bad response from server' )
    if ( $d ) {
        Write-Host $_.Exception.ToString()
    }  
    exit 
}