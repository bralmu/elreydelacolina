var refreshPeriod = 30;
var soundOption = 0;
var currentKing;
var lastKing;

function gotNewKing(){
    if(ret = (currentKing != lastKing)){
        sessionStorage.setItem('lastKing',currentKing);
    }
    return ret;    
}

function soundPlayer(){
    if(soundOption==1 && gotNewKing()){
        document.getElementById('sonido').play()
    }
}

function saveForm(){
    var nombre = document.getElementsByTagName('input')[0].value;
    var sexo = 'male';
    if (document.getElementsByTagName('input')[2].checked){
        sexo = 'female';
    }
    sessionStorage.setItem('name',nombre);
    sessionStorage.setItem('sex',sexo);  
    sessionStorage.setItem('refreshPeriod',refreshPeriod);
    sessionStorage.setItem('soundOption',soundOption);
    sessionStorage.setItem('lastKing',currentKing);
}

function restoreForm(){
    var nombre = sessionStorage.getItem('name');
    var sexo = sessionStorage.getItem('sex');
    document.getElementsByTagName('input')[0].value = nombre;
    if(sexo == 'female'){
        document.getElementsByTagName('input')[2].checked = true;
    }
    refreshPeriod = parseInt(sessionStorage.getItem('refreshPeriod')) || refreshPeriod;
    if(sessionStorage.getItem('soundOption') != null){
        soundOption = parseInt(sessionStorage.getItem('soundOption'));
    }
    lastKing = sessionStorage.getItem('lastKing');
    updateOptionMenu();
}

function realizarPeticion(){
    var nombre = document.getElementsByTagName('input')[0].value;
    nombre = nombre.substring(0,20);
    if(nombre.length == 0){
        alert("Escribe tu nombre primero");
        return false;
    }
    var sexo = 'male';
    if (document.getElementsByTagName('input')[2].checked){
        sexo = 'female';
    }
    var peticion = 'http://www.elreydelacolina.net/cgi/game?'+nombre+'&'+sexo;
    var xmlHttp = null;
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", peticion, false);
    xmlHttp.send(null);
    saveForm();
    setTimeout(function(){window.location.href = "http://www.elreydelacolina.net/cgi/game";}, 500);
    return false;
}

function autorefresh(){
    if(document.activeElement.name == "nombre"){
        setTimeout(autorefresh,1000);
    }
    else{
       saveForm();
       window.location.href = "http://www.elreydelacolina.net/cgi/game";
    }
}

function initialize(){
    currentKing = document.getElementsByTagName('h1')[0].innerHTML;
    document.getElementById('boton').onclick = function(){realizarPeticion();};
    document.getElementById("formulario").onsubmit = function(){realizarPeticion(); return false;};
    restoreForm();
    soundPlayer();
    drawVitrinas();
    setTimeout(autorefresh,refreshPeriod*1000);
}

function updateOptionMenu(){
    if (refreshPeriod==30){
        document.getElementById('opcion10s').className = 'opcion opcioninactiva';
        document.getElementById('opcion30s').className = 'opcion opcionactiva';
        document.getElementById('opcion0s').className = 'opcion opcioninactiva';
    }else if (refreshPeriod==10){
        document.getElementById('opcion10s').className = 'opcion opcionactiva';
        document.getElementById('opcion30s').className = 'opcion opcioninactiva';
        document.getElementById('opcion0s').className = 'opcion opcioninactiva';
    }else if (refreshPeriod>9999){
        document.getElementById('opcion10s').className = 'opcion opcioninactiva';
        document.getElementById('opcion30s').className = 'opcion opcioninactiva';
        document.getElementById('opcion0s').className = 'opcion opcionactiva';
    }
    
    if(soundOption==0){
        document.getElementById('opcionSonido').className = 'opcion opcioninactiva';
        document.getElementById('opcionMudo').className = 'opcion opcionactiva';
    }else if(soundOption==1){
        document.getElementById('opcionSonido').className = 'opcion opcionactiva';
        document.getElementById('opcionMudo').className = 'opcion opcioninactiva';
    }
}

function setRefresh(s){
    if (s==30 || s==10){
        refreshPeriod = s;
    }else if (s==0){
        refreshPeriod = 86400;
    }
    autorefresh();
}

function setSound(o){
    if(o==0){
        soundOption = 0;
    }else if(o==1){
        soundOption = 1;
    }
    autorefresh();
}

function drawVitrinas(){
    var cantidadVitrinas = document.getElementsByClassName('vitrina').length;
    var vitrina = null;
    for (var i = 0; i < cantidadVitrinas; i++) {
      vitrina = document.getElementsByClassName('vitrina')[i];
      var numeroCoronas = parseInt(vitrina.innerHTML);
      drawCrownsInVitrina(vitrina,numeroCoronas);
    }
}

function drawCrownsInVitrina(lienzo,cantidad){
    // distribuye las coronas en el canvas, caben 21.
    var x = 10, y = 20;
    for(var i = 1; i <= cantidad; i++){
        drawCrownInVitrina(lienzo,x,y,32,32);
        x += 42;
        if (i%7 == 0){
            x = 10;
            y += 42;
        }
    }    
}

function drawCrownInVitrina(lienzo,x,y,w,h){
    var ctx = lienzo.getContext("2d");
    var imagen = document.createElement('img');
    imagen.onload = function(){ctx.drawImage(imagen,x,y,w,h);}                  //esperar que la imagen este lista antes de poder dibujarla
    imagen.alt = 'corona';
    imagen.src = '../icon.png';
}
