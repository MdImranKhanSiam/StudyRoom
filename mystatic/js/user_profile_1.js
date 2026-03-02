// PROFILE IMAGE PREVIEW
profileUpload.addEventListener("change", e => {
const file = e.target.files[0];
if (file) {
profileImage.src = URL.createObjectURL(file);
}
});


// COVER IMAGE PREVIEW
coverUpload.addEventListener("change", e => {
const file = e.target.files[0];
if (file) {
document.querySelector('.cover-img').src = URL.createObjectURL(file);
}
});





function createPost() {
const text = document.getElementById("postText").value;
const imageInput = document.getElementById("postImage");


if (!text && !imageInput.files[0]) return;


const post = document.createElement("div");
post.className = "post";


if (text) {
const p = document.createElement("p");
p.innerText = text;
post.appendChild(p);
}


if (imageInput.files[0]) {
const img = document.createElement("img");
img.src = URL.createObjectURL(imageInput.files[0]);
post.appendChild(img);
}


document.getElementById("posts").prepend(post);


document.getElementById("postText").value = "";
imageInput.value = "";
}

// Add comment