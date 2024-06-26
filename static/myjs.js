// Berikan comment agar team paham
var isUsernameChecked = false; // Flag to check if username is checked
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

function checkid_listener() {
    $("#check-id").click(function (event) {
        check_id();
    });

}


// function untuk continue serta melihat apakah ada field yang kosong, juga mengecek jika password verify tidak sama 
function listen_continue() {
    event.preventDefault();

    var username_give = $("#username").val();
    var password_give = $("#password").val();
    var verify_password = $("#verify_password").val();

    // Check if username is checked
    if (!isUsernameChecked) {
        check_id();
        if (!isUsernameChecked) {
            return;
        }
    }

    // Check if username, password, or verify password fields are empty
    $("#id-taken").empty()
    if (password_give === "") {
        $("#password-checker").text('Please fill the password field');
        return;
    }
    $("#password-checker").empty()
    if (verify_password === "") {
        $("#password-same").text('Please verify your password');
        return;
    }

    // Verify password
    if (password_give !== verify_password) {
        $("#password-same").text('Password not the same');
        return;
    }

    $.ajax({
        url: '/api/sign_up',
        method: 'POST',
        data: {
            "username_give": username_give,
            "password_give": password_give
        },
        success: function (response) {
            // If sign-up is successful, redirect to login page or do other actions
            window.location.href = '/login';
        },
        error: function (xhr, status, error) {
            var errorMessage = xhr.responseJSON.msg;
            $("#error-message").text(errorMessage);
        }
    });

}
function listen_login_continue() {
    // Menghentikan form dari submit biasa
    event.preventDefault();

    // Mengambil nilai dari input
    var username_give = $("#username").val();  // Menyesuaikan nama variabel
    var password_give = $("#password").val();  // Menyesuaikan nama variabel

    // Melakukan permintaan AJAX ke endpoint login
    $.ajax({
        url: '/api/sign_in',
        method: 'POST',
        data: {
            "username_give": username_give,
            "password_give": password_give
        },
        success: function (response) {
            // Mengatur cookie dengan nama 'nama_cookie' dan nilai 'nilai_cookie' dengan masa kedaluwarsa 1 hari
            $.cookie('token', response["token"], { expires: 1 });

            // Jika login berhasil, redirect atau lakukan tindakan lainnya
            window.location.href = '/';
        },
        error: function (xhr, status, error) {
            // Jika login gagal, tampilkan pesan error
            console.log(error)
            console.log(status)
            console.log(xhr)
            if (error == 'NOT FOUND') {
                $("#anjim").text('Please check your username or password');
                return;
            }
        }
    });
}
function continue_button_listener() {
    $("#continueBtn").click(function (event) {
        listen_continue()
    });
}

function continue_button_listener_forgot() {
    $("#continueBtn").click(function (event) {
        listen_continue_forgot()
    });
}

function enter_listener() {
    if (event.key === 'Enter') {
        listen_continue()
    } else {
        return;
    }
}
function login_button_listener() {
    $("#loginBtn").click(function (event) {
        listen_login_continue()
    });
}
function enter_listener_login() {
    if (event.key === 'Enter') {
        // console.log("titit")
        listen_login_continue()
    } else {
        return;
    }
}

// Function untuk mengecek apakah username available

function check_id() {
    event.preventDefault();

    var username_give = $("#username").val();
    if (username_give === "") {
        $("#id-taken").text('Please fill your username first');
        return;
    }
    $.ajax({
        url: '/api/check_username',
        method: 'POST',
        data: {
            "username_give": username_give
        },
        success: function (response) {
            $("#id-taken").empty()
            if (!response.available) {
                $("#id-taken").text('Username has been taken');
            } else {
                $("#id-taken").removeClass('has-text-danger')
                $("#id-taken").addClass('has-text-success')
                $("#id-taken").text('Username available');
                isUsernameChecked = true; // Set flag to true after successful check
            }
        },
        error: function (xhr, status, error) {
            var errorMessage = xhr.responseJSON.msg;
            $("#error-message").text(errorMessage);
        }
    });
};
function search_images() {
    if (event.key === 'Enter') {
    } else {
        return;
    }
    const searchBar = $('.search-input');
    const galleryContent = $('#gallery');
    const modalsContent = $('#modals-image-fullscreen');
    const paginationParent = $('#pagination-parent-nav');
    const searchIcon = $('#search-bar-icon-index');
    searchIcon.removeClass();
    searchIcon.empty();
    searchIcon.append(`<i class="mx-1 fas fa-spinner fa-spin"></i>`);
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

            searchIcon.empty();
            searchIcon.addClass('search-icon material-symbols-outlined');
            searchIcon.text('search');
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
                        <div id="dropup-area-collection">
                            <!-- Dropup message change collection -->
                        </div>
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
                                <span class="icon ml-4" onclick="event.stopPropagation();window.location.href = '/detail/${results[idx]["_id"]}?from_page=/?page=${response['curr_page']}${response['args_nav']}'">
                                    <i class="fa-solid fa-comment"></i>
                                </span>
                `;
                if (response['is_superadmin'] || results[idx]['username'] === response['username']) {
                    // Adalah superadmin atau image ini milik user tsb
                    tempHtmlModals += `
                    <span class="icon ml-4" onclick="deleteImage('${results[idx]["_id"]}')">
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
        success: function (response) {
            window.location.reload();
        },
        error: function (xhr, status, error) {
            var errorMessage = xhr.responseJSON.msg;
            alert(errorMessage);
            buttonSaveUpload.empty();
        }
    })
}
function save_user_info_button() {
    const buttonSaveUpload = $("#button-save-upload-image-profile");
    buttonSaveUpload.empty();
    buttonSaveUpload.append(`<progress class="progress is-small is-link my-3" max="100">Uploading</progress>`);
    let bioUpload = $("#bio-upload").val();
    let genderUpload = $("#gender-upload").val();
    let fileUpload = $("#file-input-upload-profile")[0].files[0];
    let form_data = new FormData();
    form_data.append('file_give', fileUpload);
    form_data.append('bio_give', bioUpload);
    form_data.append('gender_give', genderUpload);
    let urlWithoutHash = window.location.href.split('#')[0];
    $.ajax({
        type: 'PUT',
        url: '/api/me',
        cache: false,
        processData: false,
        contentType: false,
        data: form_data,
        success: function (response, textStatus, xhr) {
            if (xhr.status == 200) {
                // Reload the page with the modified URL
                window.location.href = urlWithoutHash;
            } else {
                alert('Something went wrong ' + response["msg"]);
            }
        },
        error: function (xhr, status, error) {
            var errorMessage = xhr.responseJSON.msg;
            alert(errorMessage);
            buttonSaveUpload.empty();
        }
    })
}
function save_collection_button() {
    const buttonSaveUpload = $("#button-save-collection");
    buttonSaveUpload.empty();
    buttonSaveUpload.append(`<progress class="progress is-small is-link my-3" max="100">Uploading</progress>`);
    let collectionName = $("#collection-name-new").val();
    let chooseCollectionNew = $("#collection-choose-new").prop('checked');
    $.ajax({
        type: 'POST',
        url: '/api/collection/create',
        data: {
            "collection_name_give": collectionName,
            "choose_created_collection": chooseCollectionNew
        },
        success: function (response, textStatus, xhr) {
            if (xhr.status == 200) {
                // Reload the page
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
    $('#file-upload-images-div input[type=file]').on('change', function () {
        if (this.files.length > 0) {
            $('#file-upload-images-div .file-name').text(this.files[0].name);
        }
    });
}
function file_upload_image_namer_profile() {
    $('#file-upload-images-div-profile input[type=file]').on('change', function () {
        if (this.files.length > 0) {
            $('#file-upload-images-div-profile #file-name-profile').text(this.files[0].name);
        }
    });
}
function toggleLike(id) {
    event.stopPropagation();
    const heartLike = $('span#heart-icon-modals-fullscreen-' + id);
    heartLike.empty();
    heartLike.append(`<i class="fas fa-spinner fa-spin"></i>`);
    incrementLikes(`${id}`);
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
// Untuk page comments
function incrementLikes(id) {
    const spanCounter = $('#like-count-post');

    if (spanCounter.hasClass('has-text-danger')) {
        spanCounter.removeClass('has-text-danger');
        spanCounter.addClass('has-text-link');
        $('#like-count-post').text(function (i, text) {
            return parseInt(text) - 1;
        });
    } else {
        spanCounter.removeClass('has-text-link');
        spanCounter.addClass('has-text-danger');
        $('#like-count-post').text(function (i, text) {
            return parseInt(text) + 1;
        });
    }
}
function toggleBookmark(id) {
    event.stopPropagation();
    const bookmarkIcon = $('span#bookmark-icon-modals-fullscreen-' + id);
    bookmarkIcon.empty();
    bookmarkIcon.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/bookmark",
        type: "POST",
        data: {
            "post_id_give": id,
        },
        success: function (response) {
            bookmarkIcon.empty();
            if (response["status"] == "created") {
                messageChangeCollection(id);
                bookmarkIcon.append(`<i class="fa-solid fa-bookmark has-text-link"></i>`);
            } else {
                // resetChangeCollection(); Beri waktu user agar bisa merubah pikiran
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
            window.location.reload();
        }
    })
}
function changeBookmarkCollection(collection_id) {
    const boxIconSelect = $('#icon-box-' + collection_id);
    boxIconSelect.empty();
    boxIconSelect.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/collection/select",
        type: "PUT",
        data: {
            "collection_id_give": collection_id,
        },
        success: function (response) {
            if (response["status"] == "updated") {
                window.location.reload();
            } else {
                alert('Something went wrong ' + response["msg"]);
            }
        }
    })
}
function uploadComment(post_id = '') {
    let commentInput = $("#input-text-area-comment");
    let commentGive = commentInput.val();
    if (post_id == '' || commentGive == '') {
        commentInput.removeClass("is-info");
        commentInput.addClass("is-danger");
        commentInput.focus();
    }
    const divProgressUpload = $('#hidden-comment-upload-progress');
    divProgressUpload.append('<progress class="progress is-small is-link my-3" max="100">Uploading</progress>');
    commentInput.removeClass("is-danger");
    commentInput.addClass("is-info");
    $.ajax({
        url: "/api/comment/create",
        type: "POST",
        data: {
            "comment_give": commentGive,
            "post_id_give": post_id
        },
        success: function (response) {
            if (response["status"] == "created") {
                window.location.reload();
            } else {
                alert('Something went wrong ' + response["msg"]);
            }
        }
    })
}
function deleteComment(comment_id) {
    event.stopPropagation();
    const deleteIcon = $('#delete-icon-comment-' + comment_id);
    deleteIcon.empty();
    deleteIcon.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/comment/delete",
        type: "DELETE",
        data: {
            "comment_id_give": comment_id,
        },
        success: function (response) {
            if (response["status"] == "deleted") {
                window.location.reload();
            } else {
                alert('Something went wrong ' + response["msg"]);
            }
        }
    })
}

// Menambahkan event listener ke elemen dokumen untuk menangani event klik pada tombol
document.addEventListener('click', function (event) {
    // Periksa apakah elemen yang diklik memiliki kelas "copy-button"
    if (event.target.classList.contains('copy-button')) {
        // Dapatkan teks komentar dari atribut data-comment
        const commentText = event.target.getAttribute('data-comment');
        // Panggil fungsi untuk menyalin komentar
        copyComment(event.target, commentText);
    }
});

// Fungsi untuk menyalin komentar ke clipboard dan menampilkan pesan pemberitahuan
function copyComment(button, commentText) {
    // Buat elemen textarea sementara untuk menyalin teks
    const tempTextArea = document.createElement('textarea');
    tempTextArea.value = commentText;
    document.body.appendChild(tempTextArea);

    // Pilih teks di textarea dan salin ke clipboard
    tempTextArea.select();
    document.execCommand('copy');

    // Hapus elemen textarea sementara
    document.body.removeChild(tempTextArea);

    // Dapatkan elemen pesan pemberitahuan dari elemen parent tombol
    const copiedMessage = button.parentElement.querySelector('.copied-message');

    // Tampilkan pesan pemberitahuan
    copiedMessage.style.display = 'block';

    // Sembunyikan pesan pemberitahuan setelah beberapa detik
    setTimeout(function () {
        copiedMessage.style.display = 'none';
    }, 2000); // Pesan akan disembunyikan setelah 2 detik
}

function from_page_backtrack_listener() {
    var hash = window.location.hash; // Ambil value pagar contoh = localhost:5000/#modal-image-112233
    if (hash && hash.startsWith('#modal-image')) {
        var modalId = hash.substr(1); // Remove the "#" from the hash
        var modal = $('#' + modalId);
        if (modal.length) {
            modal.addClass('is-active'); // Add a class to show the modal
        }
    }
}
function GoBackRefresh(event) {
    if ('referrer' in document) {
        window.location = document.referrer;
        /* OR */
        //location.replace(document.referrer);
    } else {
        window.history.back();
    }
}
function from_sidebar_user_edit() {
    var hash = window.location.hash; // Ambil value pagar contoh = localhost:5000/#modal-image-112233
    if (hash && hash.startsWith('#modal-edit-info')) {
        var modalId = hash.substr(1); // Remove the "#" from the hash
        var modal = $('#' + modalId);
        if (modal.length) {
            modal.addClass('is-active'); // Add a class to show the modal
        }
    }
}
function deleteCollection(collection_id) {
    const deleteIcon = $('#icon-delete-collection-' + collection_id);
    console.log('#icon-delete-collection-' + collection_id);
    deleteIcon.empty();
    deleteIcon.append(`<i class="fas fa-spinner fa-spin"></i>`);
    $.ajax({
        url: "/api/collection/delete",
        type: "DELETE",
        data: {
            "collection_id_give": collection_id,
        },
        success: function (response) {
            window.location.reload();
        }
    })
}

function togglePassword() {
    var passwordInput = document.getElementById("password");
    var eyeIcon = document.getElementById("eye-icon");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.classList.remove("fa-eye-slash");
        eyeIcon.classList.add("fa-eye");
    } else {
        passwordInput.type = "password";
        eyeIcon.classList.remove("fa-eye");
        eyeIcon.classList.add("fa-eye-slash");
    }
}

function toggleVerifyPassword() {
    var passwordInput = document.getElementById("verify_password");
    var eyeIcon = document.getElementById("eye-icon-verify");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.classList.remove("fa-eye-slash");
        eyeIcon.classList.add("fa-eye");
    } else {
        passwordInput.type = "password";
        eyeIcon.classList.remove("fa-eye");
        eyeIcon.classList.add("fa-eye-slash");
    }
}

function listen_continue_forgot() {
    event.preventDefault();

    var username_give = $("#username").val();
    var password_give = $("#password").val();
    var verify_password = $("#verify_password").val();

    // Check if username, password, or verify password fields are empty
    $("#id-taken").empty()
    if (password_give === "") {
        $("#password-checker").text('Please fill the password field');
        return;
    }
    $("#password-checker").empty()
    if (verify_password === "") {
        $("#password-same").text('Please verify your password');
        return;
    }

    // Verify password
    if (password_give !== verify_password) {
        $("#password-same").text('Password not the same');
        return;
    }

    $.ajax({
        url: '/api/forgotpw',
        method: 'POST',
        data: {
            "username_give": username_give,
            "password_give": password_give
        },
        success: function (response) {
            // If sign-up is successful, redirect to login page or do other actions
            window.location.href = '/login';
        },
        error: function (xhr, status, error) {
            var errorMessage = xhr.responseJSON.msg;
            $("#error-message").text(errorMessage);
        }
    });
}
function toggleDropdown() {
    var dropdownMenu = document.getElementById('dropdown-menu3');
    dropdownMenu.classList.toggle('show');
 }

// Bookmark popup collection chooser
var popupTimer;
var countdownInterval;

function boxDropupCollectionListener() {
    event.stopPropagation();
    const messageBox = $('div#dropup-area-collection');
    const boxDropup = $('div#box-dropup-collection');
    var timerElement = $('span#countdown-dropup');
    if (boxDropup.hasClass('is-active')) {
        showTimeCountdown();
        popupTimer = setTimeout(function () {
            messageBox.empty();
        }, 5000); // 5 Detik
        boxDropup.removeClass('is-active');
    } else {
        clearInterval(countdownInterval);
        timerElement.empty();
        clearTimeout(popupTimer);
        boxDropup.addClass('is-active');
    }
}
function showTimeCountdown() {
    // Set the target time (in milliseconds)
    var targetTime = Date.now() + 5000; // 5 seconds from now
    var timerElement = $('span#countdown-dropup');

    // Update the countdown every second
    countdownInterval = setInterval(function () {
        // Calculate the remaining time
        var currentTime = Date.now();
        var remainingTime = targetTime - currentTime;

        // Check if the countdown is finished
        if (remainingTime <= 0) {
            clearInterval(countdownInterval); // Stop the countdown
            timerElement.empty();
            return;
        }

        // Format the remaining time (e.g., MM:SS)
        // var minutes = Math.floor(remainingTime / 60000);
        var seconds = Math.ceil((remainingTime % 60000) / 1000);
        // var formattedTime = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
        var formattedTime = seconds.toString();

        // Update the timer element with the formatted time
        timerElement.text(formattedTime);
    }, 1000); // Update every second
}
function resetChangeCollection() {
    // Reset for new post opened
    const messageBox = $('div#dropup-area-collection');
    messageBox.empty();
    var timerElement = $('span#countdown-dropup');
    clearInterval(countdownInterval);
    timerElement.empty();
    clearTimeout(popupTimer);
}
function messageChangeCollection() {
    const messageBox = $('div#dropup-area-collection');
    // Reset for new post opened
    resetChangeCollection();
    $.ajax({
        url: "/api/collections",
        type: "GET",
        data: {},
        success: function (response) {
            let data = response["data"];
            let collection_choosed = response["collection_choosed"];
            let collections_html = `
            <div class="bottom-content-notification">
                <!--  add is-hoverable class if you want some hover action -->
                <div class="box dropdown has-background-success is-right is-up has-text-black py-3"
                    id="box-dropup-collection" onclick="event.stopPropagation()">
                    <div class="dropdown-trigger" onclick="boxDropupCollectionListener()">
                        <span class="icon-text">
                            <span id="countdown-dropup"></span>
                            <span class="icon">
                                <i class="fa-solid fa-bookmark"></i>
                            </span>
                            <span>${collection_choosed}</span>
                            <span class="icon is-small mt-1">
                                <i class="fas fa-angle-up" aria-hidden="true"></i>
                            </span>
                        </span>
                    </div>
                    <div class="dropdown-menu mt-1" id="dropdown-menu4" role="menu">
                        <div class="dropdown-content">
                            <div class="dropdown-item">
            `;
            for (collection in data){
                collections_html+=`
                <span class="icon-text">
                `;
                if (collection_choosed == data[collection]['collection_name']){
                    collections_html+=`
                    <span class="icon has-text-success">
                        <i class="fa-solid fa-square-check"></i>
                    </span>
                    <span>${data[collection]['collection_name']}</span>
                </span>
                </br>`;
                } else {
                    collections_html+=`
                    <span class="icon has-text-gray" onclick="changeBookmarkCollection('${data[collection]['_id']}')" id="icon-box-${data[collection]['_id']}">
                        <i class="fa-regular fa-square"></i>
                    </span>
                    <span onclick="changeBookmarkCollection('${data[collection]['_id']}')">${data[collection]['collection_name']}</span>
                </span>
                </br>`;
                }   
            }
            collections_html+=`
                                <a href="/bookmarks">...</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            `;
            messageBox.append(collections_html);
            showTimeCountdown();
            popupTimer = setTimeout(function () {
                messageBox.empty();
            }, 5000);
        }
    })
}