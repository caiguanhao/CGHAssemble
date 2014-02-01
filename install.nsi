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

!insertmacro MUI_PAGE_LICENSE "LICENSE"
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
  WriteRegStr HKCU "Software\CGHAssemble" "" $INSTDIR
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
  DeleteRegKey /ifempty HKCU "Software\CGHAssemble"
SectionEnd
