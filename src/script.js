


let button_txt = document.getElementById("button-txt");
let txt_cadre = document.getElementById("text-loading");

function filesent() {
    txt_cadre.textContent = "Génération de l'image ...";

    // lancer le programme python 

    let img = "../points.png"
    if (!img) {
        console.log("Error, did not find image");
        txt_cadre.textContent = "Erreur, image non généré";
    }

    txt_cadre.textContent = "";



}