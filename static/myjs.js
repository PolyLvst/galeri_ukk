// Berikan comment agar team paham
function load_images() {
    const gallery = $('#gallery');

    // Example of images (you can replace with your own data)
    const images = [
        'https://via.placeholder.com/300x200',
        'https://via.placeholder.com/300x250',
        'https://via.placeholder.com/300x300',
        'https://via.placeholder.com/300x400',
        'https://via.placeholder.com/300x500',
        'https://via.placeholder.com/300x600',
        'https://via.placeholder.com/300x700',
        'https://via.placeholder.com/300x200',
        'https://via.placeholder.com/300x250',
        'https://via.placeholder.com/300x300',
        'https://via.placeholder.com/300x400',
        'https://via.placeholder.com/300x500',
        'https://via.placeholder.com/300x600',
        'https://via.placeholder.com/300x700',
        'https://via.placeholder.com/300x800'
    ];

    images.forEach(function (imageSrc) {
        const card = $('<div>').addClass('card my-2 mx-2');
        const cardImage = $('<div>').addClass('card-image');
        // const figure = $('<figure>').addClass('image');

        const img = $('<img>').attr('src', imageSrc).css('width', 200);

        // figure.append(img);
        cardImage.append(img);
        card.append(cardImage);
        gallery.append(card);
    });
};
function layout_masonry() {
    // Initialize Masonry
    var $grid = $('#gallery').masonry({
        itemSelector: '.card',
        isFitWidth: true
    });
    // Layout Masonry after each image loads (optional)
    $grid.imagesLoaded().progress(function () {
        $grid.masonry('layout');
    });
}