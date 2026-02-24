

" source https://www.pierre-giraud.com/javascript-apprendre-coder-cours/dom-acces-modification/#google_vignette"

let button_txt = document.getElementById("button-txt");
let txt_cadre = document.getElementById("text-loading");

function filesent() {
    let inputFichier = document.getElementById("point-txt");

    if (inputFichier.value == "") {
        txt_cadre.textContent = "Aucun fichiers selectioner";
    } else {
        
            
            
            txt_cadre.textContent = "";
            
            
            let zoneImage = document.querySelector(".diagramme a");
        
            zoneImage.innerHTML = "<img src='voronoi_cheick/placer_point.png' style='width: 100%; height: 100%; object-fit: contain;'>";
            
        ;}
    
    
}

function downloadimage() {

    // recupère la value du type image (png ou svg)

    // verifie si elle existe

    // lance fonction python avec le paramètre
}