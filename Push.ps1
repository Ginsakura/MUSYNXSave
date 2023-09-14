if ($args[1] -eq 'rc'){
  $version = (py -c "import MusyncSavDecodeGUI;print(MusyncSavDecodeGUI.version)")
  $release = 'Release'
}elseif($args[1] -eq 'pre'){
  $version = (py -c "import MusyncSavDecodeGUI;print(MusyncSavDecodeGUI.preVersion)")
  $release = 'PreRelease'
}else{
  $version = (py -c "import MusyncSavDecodeGUI;print(MusyncSavDecodeGUI.preVersion)")
  $release = 'NotRelease'
}
$str = $version+'  '+$args[0]+'  '+$release

git add .
echo $str
git commit -m $str
git push
git pull