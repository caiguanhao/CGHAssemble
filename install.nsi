!include "MUI2.nsh"

!define APP_NAME "CGHAssemble"
!define APP_DESC "A stupid Assemble tool."
!define APP_VER "1.0.0.0"
!define APP_AUTHOR "caiguanhao"

Name "${APP_NAME}"
BRANDINGTEXT "${APP_NAME} ${APP_VER}"
OutFile "${APP_NAME}-setup.exe"

VIProductVersion "${APP_VER}"
VIAddVersionKey /LANG=1033 "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=1033 "Comments" "${APP_DESC}"
VIAddVersionKey /LANG=1033 "CompanyName" "${APP_AUTHOR}"
VIAddVersionKey /LANG=1033 "LegalTrademarks" "Copyright (c) ${APP_AUTHOR}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Copyright (c) ${APP_AUTHOR}"
VIAddVersionKey /LANG=1033 "FileDescription" "${APP_DESC}"
VIAddVersionKey /LANG=1033 "FileVersion" "${APP_VER}"

SetCompressor /FINAL /SOLID lzma

InstallDir "$PROGRAMFILES\${APP_NAME}"

InstallDirRegKey HKCU "Software\${APP_NAME}" ""

RequestExecutionLevel admin

!define MUI_ABORTWARNING

!define MUI_ICON "res/hammer.ico"
!define MUI_UNICON "res/hammer.ico"

!define MUI_PAGE_CUSTOMFUNCTION_SHOW licpageshow

Function licpageshow
  FindWindow $0 "#32770" "" $HWNDPARENT
  CreateFont $1 "Courier" "8"
  GetDlgItem $0 $0 1000
  SendMessage $0 ${WM_SETFONT} $1 1
FunctionEnd

!insertmacro MUI_PAGE_LICENSE "LICENSES"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Program Files" SecProgramFiles
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "dist\${APP_NAME}\*"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_NAME}.exe" ""
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" \
    "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
    "$INSTDIR\${APP_NAME}.exe" "" "$INSTDIR\${APP_NAME}.exe" 0
  WriteRegStr HKLM "Software\${APP_NAME}" "" $INSTDIR
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "DisplayName" "${APP_NAME} (remove only)"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "DisplayIcon" "$INSTDIR\res\hammer.ico"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "Publisher" "${APP_AUTHOR}"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
    "Comments" "${APP_DESC}"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

LangString DESC_SecProgramFiles ${LANG_ENGLISH} \
  "Contains necessary program files required by the software."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecProgramFiles} $(DESC_SecProgramFiles)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
  RMDir /r "$INSTDIR\*.*"
  RMDir "$INSTDIR"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\*.*"
  RmDir  "$SMPROGRAMS\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
  DeleteRegKey HKLM \
    "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd
