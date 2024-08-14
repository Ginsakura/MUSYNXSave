$message = Read-Host -Prompt "Input Commit Message"
$message = $message.Split("//")
echo $message[0]
echo ===========
echo $message[-1]
echo ===========
if ($message[-1] -eq 'rc'){
  $version = (py -c "import Launcher;print(Launcher.version)")
  $release = 'Release'
}elseif($message[-1] -eq 'pre'){
  $version = (py -c "import Launcher;print(Launcher.preVersion)")
  $release = 'PreRelease'
}else{
  $version = (py -c "import Launcher;print(Launcher.preVersion)")
  $release = '[no ci]'
}
if ($message[0] -eq ""){
  $message[0] = "null"
}
$str = $version+'  '+$message[0]+'  '+$release

echo $str
git pull
git add .
git commit -m $str
git push
# git tag -a $version -m $message[0]
Read-Host -Prompt "Press Enter to exit"