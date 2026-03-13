console.log("Script loaded");

document.addEventListener("DOMContentLoaded", function () {

/* DARK MODE */

const toggleBtn = document.getElementById("theme-toggle");

if(toggleBtn){

if(localStorage.getItem("theme") === "dark"){
document.body.classList.add("dark-mode");
toggleBtn.textContent="☀️";
}

toggleBtn.addEventListener("click", ()=>{

document.body.classList.toggle("dark-mode");

if(document.body.classList.contains("dark-mode")){
localStorage.setItem("theme","dark");
toggleBtn.textContent="☀️";
}else{
localStorage.setItem("theme","light");
toggleBtn.textContent="🌙";
}

});

}

/* MENU */

const menuBtn=document.getElementById("menu-btn");
const menu=document.getElementById("nav-links");

if(menuBtn && menu){

menuBtn.addEventListener("click",function(e){

e.stopPropagation();
menu.classList.toggle("open");

});

document.addEventListener("click",function(e){

if(!menu.contains(e.target) && !menuBtn.contains(e.target)){
menu.classList.remove("open");
}

});

}

/* ACTIVE LINK */

const links=document.querySelectorAll(".nav-item");

links.forEach(link=>{

if(window.location.pathname === new URL(link.href).pathname){
link.classList.add("active");
}

});

});