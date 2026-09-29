const $=id=>document.getElementById(id);const KEY='localcodeeditor.files.v1';let files=[];let active='';let timer;
function uid(){return 'f'+Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
function save(){localStorage.setItem(KEY,JSON.stringify(files));$('saveState').textContent='Saved locally';clearTimeout(timer);timer=setTimeout(()=>$('saveState').textContent='Ready',1400)}
function current(){return files.find(f=>f.id===active)}
function render(){const list=$('fileList');list.innerHTML='';files.forEach(f=>{const li=document.createElement('li');li.textContent=f.name;li.className=f.id===active?'active':'';li.onclick=()=>select(f.id);list.append(li)});const f=current();$('activeName').textContent=f?f.name:'No file selected';$('editor').value=f?f.content:'';$('editor').disabled=!f;$('deleteBtn').disabled=!f;$('renameBtn').disabled=!f}
function select(id){active=id;render()}
function create(name='untitled.html',content=''){const f={id:uid(),name,content};files.push(f);active=f.id;save();render()}
$('newFile').onclick=()=>{const name=prompt('File name','untitled.html');if(name&&name.trim())create(name.trim())};
$('editor').addEventListener('input',()=>{const f=current();if(!f)return;f.content=$('editor').value;save()});
$('renameBtn').onclick=()=>{const f=current();if(!f)return;const name=prompt('New file name',f.name);if(name&&name.trim()){f.name=name.trim();save();render()}};
$('deleteBtn').onclick=()=>{const f=current();if(!f||!confirm(`Delete ${f.name}?`))return;files=files.filter(x=>x.id!==active);active=files[0]?.id||'';save();render()};
$('exportFile').onclick=()=>{const f=current();if(!f)return;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([f.content],{type:'text/plain'}));a.download=f.name;a.click();URL.revokeObjectURL(a.href)};
$('importFile').onclick=()=>$('filePicker').click();$('filePicker').onchange=async e=>{const file=e.target.files[0];if(!file)return;create(file.name,await file.text());e.target.value=''};
$('previewBtn').onclick=()=>{const f=current();if(!f)return;$('preview').srcdoc=f.content;$('preview').parentElement.classList.remove('hidden')};$('closePreview').onclick=()=>$('preview').parentElement.classList.add('hidden');
try{files=JSON.parse(localStorage.getItem(KEY)||'[]')}catch{files=[]}if(!files.length){files=[{id:uid(),name:'index.html',content:'<!doctype html>\n<html>\n<body>\n  <h1>Hello, LocalCodeEditor!</h1>\n  <p>Your files are stored in this browser.</p>\n</body>\n</html>'}];save()}active=files[0]?.id||'';render();
if('serviceWorker'in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));