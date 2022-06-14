const titleInput = document.querySelector('input(name=title');
const slugInput = document.querySelector('input(name=slug)');

const slugify = (val) => {
    return val.toString().toLowerCase().trim()
        .replace(/&/g, '-and-') // & replaced with and
        .replace(/[\s\W-]+/g, '-') //non-word chars replaced with -
};

titleInput.addEventListener('keyup', (e) => {
    slugInput.setAttribute('value', slugify(titleInput.value));
});