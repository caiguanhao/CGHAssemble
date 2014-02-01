!include "MUI2.nsh"

Name "CGHAssemble"
OutFile "CGHAssemble-setup.exe"

SetCompressor /FINAL /SOLID lzma

InstallDir "$PROGRAMFILES\CGHAssemble"

InstallDirRegKey HKCU "Software\CGHAssemble" ""

RequestExecutionLevel user

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
  File /r "dist\CGHAssemble\*"
  CreateShortCut "$DESKTOP\CGHAssemble.lnk" "$INSTDIR\CGHAssemble.exe" ""
  CreateDirectory "$SMPROGRAMS\CGHAssemble"
  CreateShortCut "$SMPROGRAMS\CGHAssemble\Uninstall CGHAssemble.lnk" \
    "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\CGHAssemble\CGHAssemble.lnk" \
    "$INSTDIR\CGHAssemble.exe" "" "$INSTDIR\CGHAssemble.exe" 0
  WriteRegStr HKLM "Software\CGHAssemble" "" $INSTDIR
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\CGHAssemble" \
    "DisplayName" "CGHAssemble (remove only)"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\CGHAssemble" \
    "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\CGHAssemble" \
    "DisplayIcon" "$INSTDIR\res\hammer.ico"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\CGHAssemble" \
    "Publisher" "caiguanhao"
  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\CGHAssemble" \
    "Comments" "A stupid Assemble tool."
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
  Delete "$DESKTOP\CGHAssemble.lnk"
  Delete "$SMPROGRAMS\CGHAssemble\*.*"
  RmDir  "$SMPROGRAMS\CGHAssemble"
  DeleteRegKey HKLM "Software\CGHAssemble"
  DeleteRegKey HKLM \
    "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CGHAssemble"
SectionEnd
