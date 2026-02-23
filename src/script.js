


let button_txt = document.getElementById("button-txt");
let txt_cadre = document.getElementById("text-loading");

function filesent() {
    txt_cadre.textContent = "Génération de l'image ...";

    //crée variable qui récupère le fichier

    // lancer le programme python avec en paramètre le fichier

    let img = "../points.png"
    if (!img) {
        console.log("Error, did not find image");
        txt_cadre.textContent = "Erreur, image non généré";
    }

    txt_cadre.textContent = "";

    // affiche image
}

function downloadimage() {

    // recupère la value du type image (png ou svg)

    // verifie si elle existe

    // lance fonction python avec le paramètre
}