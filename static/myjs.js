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
    if (event.key === 'Enter') {
    } else {
        return;
    }
    const searchBar = $('.search-input');
    const galleryContent = $('#gallery');
    const modalsContent = $('#modals-image-fullscreen');
    const paginationParent = $('#pagination-parent-nav');
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
                galleryContent.append(tempHtml).masonry('appended', tempHtml);
                galleryContent.masonry('reloadItems');
                galleryContent.masonry('layout');
                let tempHtmlModals = `
                <div id="modal-image-${results[idx]["_id"]}" class="modal modal-fx-superScaled">
                    <div class="modal-background">
                        <div class="mx-4 column box bottom-content has-text-centered">
                            <span class="icon" id="bookmark-icon-modals-fullscreen-${results[idx]["_id"]}") onclick="toggleBookmark('${results[idx]["_id"]}')"">
                `;
                if (results[idx]["bookmark_by_me"]) {
                    tempHtmlModals += `<i class="fa-solid fa-bookmark has-text-link"></i>`;
                } else {
                    tempHtmlModals += `<i class="fa-regular fa-bookmark"></i>`;
                };
                tempHtmlModals += `</span>
                            <span class="icon ml-4" id="heart-icon-modals-fullscreen-${results[idx]["_id"]}" onclick="toggleLike('${results[idx]["_id"]}')"">
                `;
                if (results[idx]["like_by_me"]) {
                    tempHtmlModals += `<i class="fa-solid fa-heart has-text-danger"></i>`;
                } else {
                    tempHtmlModals += `<i class="fa-regular fa-heart"></i>`;
                };
                tempHtmlModals += `</span>
                                <span class="icon ml-4" onclick="alert('Commented')">
                                    <i class="fa-solid fa-comment"></i>
                                </span>
                `;
                if (response['is_superadmin'] || results[idx]['username'] === response['username']) {
                    // Adalah superadmin atau image ini milik user tsb
                    tempHtmlModals += `
                    <span class="icon ml-4" onclick="alert('Deleted')">
                    <i class="fa-solid fa-trash"></i>
                    </span>
                    `;
                }
                tempHtmlModals += `
                        </div>
                    </div>
                    <div class="modal-content is-image">
                        <img loading="lazy" class="lazy-load" src="${results[idx]['image']}" alt="Photos by ${results[idx]['username']}">
                    </div>
                    <button class="modal-close is-large" aria-label="close"></button>
                </div>
                `;
                modalsContent.append(tempHtmlModals);

            }
            // Pagination adalah navigasi bawah yg menunjukkan halaman berapa user berada
            let paginationHtml = ``;
            // Jika ada halaman sebelumnya
            if (response['prev_page']) {
                paginationHtml += `<a href="/?query=${searchBarContent}&page=${response['prev_page']}" class="pagination-previous">Previous</a>`;
            } else {
                paginationHtml += `<a class="pagination-previous is-disabled">Previous</a>`;
            }
            // Jika ada halaman selanjutnya
            if (response['next_page']) {
                paginationHtml += `<a href="/?query=${searchBarContent}&page=${response['next_page']}" class="pagination-next">Next page</a>`;
            } else {
                paginationHtml += `<a class="pagination-next is-disabled">Next page</a>`;
            }
            paginationHtml += `
            <ul class="pagination-list">
                <li><a href="/?query=${searchBarContent}&page=1" class="pagination-link">1</a></li>

                <li><span class="pagination-ellipsis">&hellip;</span></li>
            `;
            if (response['prev_page']) {
                paginationHtml += `<li><a href="/?query=${searchBarContent}&page=${response['prev_page']}" class="pagination-link">${response['prev_page']}</a></li>`;
            }
            paginationHtml += `<li><a class="pagination-link is-current" id="is-current-page-number">${response['curr_page']}</a></li>`;
            if (response['next_page']) {
                paginationHtml += `<li><a href="/?query=${searchBarContent}&page=${response['next_page']}" class="pagination-link">${response['next_page']}</a></li>`;
            }
            paginationHtml += `
                <li><span class="pagination-ellipsis">&hellip;</span></li>
                <li><a href="/?query=${searchBarContent}&page=${response['end_page']}" class="pagination-link">${response['end_page']}</a></li>
            </ul>`;
            paginationParent.empty();
            paginationParent.append(paginationHtml);
            reloadModalScript();
        }
    })
}
function search_images_redirect() {
    if (event.key === 'Enter') {
    } else {
        return;
    }
    const searchBar = $('.search-input');
    // Ambil value search bar
    let searchBarContent = searchBar.val();
    window.location.href = `/?query=${searchBarContent}`;
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
function upload_button() {
    const buttonSaveUpload = $("#button-save-upload-image");
    buttonSaveUpload.empty();
    buttonSaveUpload.append(`<progress class="progress is-small is-link my-3" max="100">Uploading</progress>`);
    let judulUpload = $("#judul-upload").val();
    let deskripsiUpload = $("#deskripsi-upload").val();
    let fileUpload = $("#file-input-upload")[0].files[0];
    let kategori = getSelectedTags();
    let form_data = new FormData();
    form_data.append('file_give', fileUpload);
    form_data.append('title_give', judulUpload);
    form_data.append('deskripsi_give', deskripsiUpload);
    form_data.append('kategori_give', kategori);
    $.ajax({
        type: 'POST',
        url: '/api/images/create',
        cache: false,
        processData: false,
        contentType: false,
        data: form_data,
        success: function (response, textStatus, xhr) {
            if (xhr.status == 200) {
                window.location.reload();
            } else {
                alert('Something went wrong ' + response["msg"]);
            }
        }
    })
}
function getSelectedTags() {
    let selectedTags = [];
    $('.tags-list-unique.is-success').each(function () {
        selectedTags.push($(this).text().trim());
    });
    return selectedTags;
}
function toggleTags(targetId, tagsName) {
    let target = $("#" + targetId);
    if (target.hasClass("is-success")) {
        target.removeClass("is-success");
        target.addClass("is-danger");
        $('#delete-tags-kategori-' + tagsName).remove();
    } else {
        target.removeClass("is-danger");
        target.addClass("is-success");
        $('#delete-tags-kategori-' + tagsName).remove();
        target.append(`<button class="delete is-small" id="delete-tags-kategori-${tagsName}"></button>`)
    }
}
function file_upload_image_namer() {
    const fileInput = document.querySelector("#file-upload-images-div input[type=file]");
    fileInput.onchange = () => {
        if (fileInput.files.length > 0) {
            const fileName = document.querySelector("#file-upload-images-div .file-name");
            fileName.textContent = fileInput.files[0].name;
        }
    };
}
function toggleLike(id) {
    event.stopPropagation();
    const heartLike = $('#heart-icon-modals-fullscreen-' + id);
    heartLike.empty();
    heartLike.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/like",
        type: "POST",
        data: {
            "post_id_give": id,
        },
        success: function (response) {
            heartLike.empty();
            if (response["status"] == "created") {
                heartLike.append(`<i class="fa-solid fa-heart has-text-danger"></i>`);
            } else {
                heartLike.append(`<i class="fa-regular fa-heart"></i>`);
            }
        }
    })
}
function toggleBookmark(id) {
    event.stopPropagation();
    const bookmarkIcon = $('#bookmark-icon-modals-fullscreen-' + id);
    bookmarkIcon.empty();
    bookmarkIcon.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/bookmark",
        type: "POST",
        data: {
            "post_id_give": id,
            "collection_id_give": "65ffb738b96613c66b748e1b"
        },
        success: function (response) {
            bookmarkIcon.empty();
            if (response["status"] == "created") {
                bookmarkIcon.append(`<i class="fa-solid fa-bookmark has-text-link"></i>`);
            } else {
                bookmarkIcon.append(`<i class="fa-regular fa-bookmark"></i>`);
            }
        }
    })
}
function deleteImage(id) {
    event.stopPropagation();
    const deleteIcon = $('#delete-icon-modals-fullscreen-' + id);
    deleteIcon.empty();
    deleteIcon.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/images/delete",
        type: "DELETE",
        data: {
            "image_id_give": id,
        },
        success: function (response) {
            window.location.href = '/';
        }
    })
}