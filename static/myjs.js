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
    // Initialize Masonry
    let mason_layout = $('#gallery').masonry({
        itemSelector: '.card',
        isFitWidth: true
    });
    mason_layout.imagesLoaded().progress(function () {
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

function continue_button_listener() {
    $("#continueBtn").click(function (event) {
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
    });

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
}