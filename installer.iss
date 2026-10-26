#ifndef SourceDir
  #define SourceDir "dist\TranslateOffline"
#endif
#define AppName "תרגום אופליין"
#define AppVersion "1.0.0"
#define WebView2Key "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"

[Setup]
AppId={{6F3B2A1E-8C4D-4E5F-9A7B-2D1C0E9F8A61}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=ariel600
AppPublisherURL=https://github.com/ariel600/translate-offline
DefaultDirName={localappdata}\Programs\TranslateOffline
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=dist
OutputBaseFilename=translate-offline-setup
Compression=lzma2
SolidCompression=yes
LZMAUseSeparateProcess=yes
DiskSpanning=yes
DiskSliceSize=2000000000
WizardStyle=modern
LicenseFile=LICENSE
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\icon.ico
SetupIconFile=assets\icon.ico

[Languages]
Name: "he"; MessagesFile: "compiler:Languages\Hebrew.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD-PARTY-NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: NeedsWebView2

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{tmp}\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; Parameters: "/silent /install"; StatusMsg: "מתקין את רכיב התצוגה של Windows..."; Check: NeedsWebView2; Flags: waituntilterminated
Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function HasWebView2(Root: Integer; Key: String): Boolean;
var
  Version: String;
begin
  Result := RegQueryStringValue(Root, Key, 'pv', Version) and (Version <> '') and (Version <> '0.0.0.0');
end;

function NeedsWebView2: Boolean;
begin
  Result := not (HasWebView2(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{#WebView2Key}')
    or HasWebView2(HKLM, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{#WebView2Key}')
    or HasWebView2(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{#WebView2Key}'));
end;
