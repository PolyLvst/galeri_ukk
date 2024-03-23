// Berikan comment agar team paham
function burger_function() {
    document.addEventListener('DOMContentLoaded', () => {
        // Get all "navbar-burger" elements
        const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
        // Add a click event on each of them
        $navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                // Get the target from the "data-target" attribute
                const target = el.dataset.target;
                const $target = document.getElementById(target);
                // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
                el.classList.toggle('is-active');
                $target.classList.toggle('is-active');
            });
        });
    });
};
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
    options_masonry = {
        // Tiap tiap gambar dengan class berikut dianggap masuk ke layout
        itemSelector: '.grid-items-masonry',
        // Responsive
        isFitWidth: true
    }
    // Initialize Masonry ke div dengan id gallery
    var mason_layout = $('#gallery').masonry(options_masonry);
    // Tunggu sampai foto telah terload semua
    mason_layout.imagesLoaded().progress(function () {
        // Aplikasikan layout ke element
        mason_layout.masonry('layout');
    });
};
function render_users_infos() {
    let profile_picture = $('#user-profile-picture');
    let sidebar_pp = $('#sidebar-user-profile-picture');
    let sidebar_username = $('#sidebar-username');
    let sidebar_about = $('#sidebar-user-about');
    let sidebar_gender = $('#sidebar-user-gender');

    $.ajax({
        url: "/api/me",
        type: "GET",
        data: {},
        success: function (response) {
            let data = response["data"];
            let username = data["username"];
            let profile_pic = data["profile_pic"];
            let bio_about = data["bio"];
            let user_gender = data["gender"];
            profile_picture.empty();
            profile_picture.append(`<img class="is-rounded" src="${profile_pic}">`)
            sidebar_pp.empty();
            sidebar_pp.append(`<img class="is-rounded" src="${profile_pic}">`)
            sidebar_username.empty();
            sidebar_username.append(`<p class="has-text-weight-bold">${username}</p>`)
            sidebar_about.empty();
            sidebar_about.append(`${bio_about}`)
            sidebar_gender.empty();
            sidebar_gender.append(`${user_gender}`)
        },
        error: function (xhr, status, error) {
            console.error("Error:", error); // Log any errors to the console
        }
    })

}
function sidebar_toggle() {
    const sidebar = $('.sidebar');
    const overlay = $('.overlay');
    if (sidebar.hasClass("open")) {
        sidebar.removeClass('open');
        overlay.css('display', 'none');
    } else {
        sidebar.addClass('open');
        overlay.css('display', 'block');
    }
}
function sidebar_listener() {
    $(".sidebar-listener").click(function () { sidebar_toggle() })
}
function search_images() {
    const searchBar = $('.search-input');
    const galleryContent = $('#gallery');
    const modalsContent = $('#modals-image-fullscreen');
    // Ambil value search bar
    let searchBarContent = searchBar.val();
    $.ajax({
        url: "/api/search?query=" + searchBarContent,
        type: "GET",
        data: {},
        success: function (response) {
            let results = response["results"];
            galleryContent.empty();
            modalsContent.empty();
            for (idx in results) {
                let tempHtml = `
                <div class="card my-2 mx-2 modal-button grid-items-masonry" data-target="modal-image-${results[idx]["_id"]}">
                    <div class="card-image">
                        <img src="${results[idx]['image_thumbnail']}" alt="Photos by ${results[idx]['username']}"
                            style="width: 200px;" class="view-image">
                    </div>
                </div>
                `;
                let tempHtmlModals = `
                <div id="modal-image-${results[idx]["_id"]}" class="modal modal-fx-superScaled">
                    <div class="modal-background">
                        <div class="mx-4 column box bottom-content has-text-centered">
                            <span class="icon" onclick="alert('Bookmarked')">
                                <i class="fa-regular fa-bookmark"></i>
                                <i class="fa-solid fa-bookmark has-text-link"></i>
                            </span>
                            <span class="icon ml-4" onclick="alert('Liked')">
                                <i class="fa-regular fa-heart"></i>
                                <i class="fa-solid fa-heart has-text-danger"></i>
                            </span>
                            <span class="icon ml-4" onclick="alert('Commented')">
                                <i class="fa-solid fa-comment"></i>
                            </span>
                `;
                if (response['is_superadmin'] || results[idx]['username'] === response['current_username']){
                    // Adalah superadmin atau image ini milik user tsb
                    tempHtmlModals+=`
                    <span class="icon ml-4" onclick="alert('Deleted')">
                    <i class="fa-solid fa-trash"></i>
                    </span>
                    `;
                }
                tempHtmlModals+=`
                        </div>
                    </div>
                    <div class="modal-content is-image">
                        <img loading="lazy" class="lazy-load" src="${results[idx]['image']}" alt="Photos by ${results[idx]['username']}">
                    </div>
                    <button class="modal-close is-large" aria-label="close"></button>
                </div>
                `;
                modalsContent.append(tempHtmlModals);
                galleryContent.append(tempHtml).masonry('appended', tempHtml);
                galleryContent.masonry('reloadItems');
                galleryContent.masonry('layout');
            }
            reloadModalScript();
        }
    })
}
function reloadModalScript() {
    $('script[src="../static/modal-fx.min.js"]').remove();
    $('<script>').attr('src', '../static/modal-fx.min.js').appendTo('body');
}
function logout_account() {
    console.log("Logging out")
    $.removeCookie('token', { path: '/' });
    console.log("logged out")
    window.location.href = "/login"
}