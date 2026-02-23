


let button_txt = document.getElementById("button-txt");
let txt_cadre = document.getElementById("text-loading");

function filesent() {
    let inputFichier = document.getElementById("point-txt");

    if (inputFichier.value == "") {
        txt_cadre.textContent = "Aucun fichiers selectioner";
    } else {
        txt_cadre.textContent = "Génération de l'image ...";}

    
}

function downloadimage() {

    // recupère la value du type image (png ou svg)

    // verifie si elle existe

    // lance fonction python avec le paramètre
}