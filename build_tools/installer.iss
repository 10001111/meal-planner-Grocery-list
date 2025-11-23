; Inno Setup Script for Meal Planner & Grocery List Generator
; Download Inno Setup from: https://jrsoftware.org/isdl.php

#define MyAppName "Meal Planner & Grocery List Generator"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName "MealPlanner.exe"

[Setup]
; Application information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MealPlanner
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=MealPlanner_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Minimum Windows version
MinVersion=6.1sp1

; License and info files (optional)
; LicenseFile=LICENSE.txt
; InfoBeforeFile=README.txt

; Icons (optional - uncomment if you have an icon file)
; SetupIconFile=cooking.ico
; UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable and all files from dist folder
Source: "dist\MealPlanner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (if user selected this option)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Optionally run the app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom message for first-time users
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Welcome to Meal Planner & Grocery List Generator Setup!' + #13#10 + #13#10 +
         'This installer will guide you through the installation process.' + #13#10 + #13#10 +
         'The app includes:' + #13#10 +
         '  - 8 pre-loaded everyday recipes' + #13#10 +
         '  - Automatic meal planning' + #13#10 +
         '  - Smart grocery list generation' + #13#10 +
         '  - Pantry inventory tracking' + #13#10 +
         '  - PDF recipe export',
         mbInformation, MB_OK);
end;
