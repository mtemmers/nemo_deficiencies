#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#define AppName "NEMO Deficiencies"
#define AppPublisher "mtemmers"
#define AppURL "https://github.com/mtemmers/nemo_deficiencies"
#define AppExeName "NEMO Deficiencies.exe"

[Setup]
AppId={{F3F318AA-6E4F-4F6C-9BF7-DB70CE97CE19}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={localappdata}\Programs\NEMO Deficiencies
DefaultGroupName=NEMO Deficiencies
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\release
OutputBaseFilename=NEMO-Deficiencies-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
UninstallDisplayIcon={app}\{#AppExeName}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Aufgaben:"
Name: "autostart"; Description: "NEMO Deficiencies bei der Anmeldung starten"; GroupDescription: "Zusätzliche Aufgaben:"

[Files]
Source: "..\dist\NEMO Deficiencies\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NEMO Deficiencies"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\NEMO Deficiencies"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userstartup}\NEMO Deficiencies"; Filename: "{app}\{#AppExeName}"; Tasks: autostart

[Run]
Filename: "{app}\{#AppExeName}"; Description: "NEMO Deficiencies starten"; Flags: nowait postinstall skipifsilent
