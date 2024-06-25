const tagsContainers = document.querySelectorAll('.tags_container');
tagsContainers.forEach(container => {
    const tags = container.querySelectorAll('.tag');
    const uniqueTags = new Set();
    tags.forEach(tag => {
        const tagText = tag.textContent.trim();
        if (uniqueTags.has(tagText)) {
            tag.nextElementSibling.remove(); 
            tag.remove();
        } else uniqueTags.add(tagText);
    });
});

$(document).ready(function() {
    $('#select2').select2({
        allowClear: true
    });
});