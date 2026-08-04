(function () {
  "use strict";

  var folders = {
    home: {
      path: "home",
      crumb: "Home",
      items: [
        { icon: "📁", name: "Movies", key: "movies" },
        { icon: "📁", name: "Shows", key: "shows" },
        { icon: "📁", name: "Books", key: "books" },
        { icon: "📁", name: "SteamLibrary", key: "steam" }
      ]
    },
    movies: {
      path: "home/Movies",
      crumb: "Movies",
      items: [
        { icon: "🎬", name: "Movie 1", key: "home" },
        { icon: "▶", name: "video1.mp4", key: "home" },
        { icon: "▶", name: "video2.mkv", key: "home" },
        { icon: "⬅", name: "Go Back", key: "home" }
      ]
    },
    shows: {
      path: "home/Shows",
      crumb: "Shows",
      items: [
        { icon: "📁", name: "Show 1", key: "home" },
        { icon: "📁", name: "Show 2", key: "home" },
        { icon: "▶", name: "Episode 1.mp4", key: "home" },
        { icon: "⬅", name: "Go Back", key: "home" }
      ]
    },
    books: {
      path: "home/Books",
      crumb: "Books",
      items: [
        { icon: "📁", name: "Book 1", key: "home" },
        { icon: "📄", name: "Part 1.pdf", key: "home" },
        { icon: "📄", name: "Part 2.pdf", key: "home" },
        { icon: "⬅", name: "Go Back", key: "home" }
      ]
    },
    steam: {
      path: "home/SteamLibrary",
      crumb: "SteamLibrary",
      items: [
        { icon: "🎮", name: "common/", key: "home" },
        { icon: "📄", name: "libraryfolders.vdf", key: "home" },
        { icon: "📁", name: "steamapps", key: "home" },
        { icon: "⬅", name: "Go Back", key: "home" }
      ]
    }
  };

  var grid = document.getElementById("tileGrid");
  var breadcrumb = document.getElementById("breadcrumb");
  var urlPath = document.getElementById("urlPath");

  if (!grid || !breadcrumb || !urlPath) return;

  function render(key) {
    var folder = folders[key] || folders.home;
    breadcrumb.textContent = folder.crumb;
    urlPath.textContent = folder.path;
    grid.innerHTML = "";

    folder.items.forEach(function (item) {
      var tile = document.createElement("button");
      tile.type = "button";
      tile.className = "tile";
      tile.setAttribute("data-key", item.key);
      tile.innerHTML =
        '<span class="tile-icon" aria-hidden="true">' + item.icon + '</span>' +
        '<span class="tile-name">' + item.name + '</span>';
      tile.addEventListener("click", function () {
        render(item.key);
      });
      grid.appendChild(tile);
    });
  }

  render("home");
})();
