function disable() {
  var x = document.getElementById("type").options[1].disabled = true;
}

function enable() {
  var x = document.getElementById("type").options[1].disabled = false;
}

function toggle(el){
    var idx = el.selectedIndex;
    if (idx != 0){
        disable();
        document.getElementById('type').value="POSITION";
    }
    else {
        enable();
    }
}

