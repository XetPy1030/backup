let p_mega;

YUI.add(
  "moodle-core_filepicker",
  function (Y) {
    Y.Node.prototype.getStylePx = function (attr) {
      var style = this.getStyle(attr);
      if ("" + style == "0" || "" + style == "0px") {
        return 0;
      }
      var matches = style.match(/^([\d\.]+)px$/);
      if (matches && parseFloat(matches[1])) {
        return parseFloat(matches[1]);
      }
      return null;
    };
    Y.Node.prototype.addClassIf = function (className, condition) {
      if (condition) {
        this.addClass(className);
      } else {
        this.removeClass(className);
      }
      return this;
    };
    Y.Node.prototype.setStyleAdv = function (stylename, value) {
      var stylenameCap =
        stylename.substr(0, 1).toUpperCase() +
        stylename.substr(1, stylename.length - 1).toLowerCase();
      this.setStyle(
        stylename,
        "" + Math.max(value, this.getStylePx("min" + stylenameCap)) + "px"
      );
      return this;
    };
    Y.Node.prototype.setImgSrc = function (src, realsrc, lazyloading) {
      if (realsrc) {
        if (M.core_filepicker.loadedpreviews[realsrc]) {
          this.set("src", realsrc).addClass("realpreview");
          return this;
        } else {
          if (!this.get("id")) {
            this.generateID();
          }
          lazyloading[this.get("id")] = realsrc;
        }
      }
      this.set("src", src);
      return this;
    };
    Y.Node.prototype.setImgRealSrc = function (lazyloading) {
      if (this.get("id") && lazyloading[this.get("id")]) {
        var newsrc = lazyloading[this.get("id")];
        M.core_filepicker.loadedpreviews[newsrc] = !0;
        this.set("src", newsrc).addClass("realpreview");
        delete lazyloading[this.get("id")];
        var treenode = this.ancestor(".fp-treeview");
        if (treenode && treenode.get("parentNode").treeview) {
          treenode
            .get("parentNode")
            .treeview.getRoot()
            .refreshPreviews(this.get("id"), newsrc);
        }
      }
      return this;
    };
    Y.YUI2.widget.Node.prototype.refreshPreviews = function (
      imgid,
      newsrc,
      regex
    ) {
      if (!regex) {
        regex = new RegExp('<img\\s[^>]*id="' + imgid + '"[^>]*?(/?)>', "im");
      }
      if (this.expanded || this.isLeaf) {
        var html = this.getContentHtml();
        if (html && this.setHtml && regex.test(html)) {
          var newhtml = this.html.replace(
            regex,
            '<img id="' +
              imgid +
              '" src="' +
              newsrc +
              '" class="realpreview"$1>',
            html
          );
          this.setHtml(newhtml);
          return !0;
        }
        if (!this.isLeaf && this.children) {
          for (var c in this.children) {
            if (this.children[c].refreshPreviews(imgid, newsrc, regex)) {
              return !0;
            }
          }
        }
      }
      return !1;
    };
    Y.Node.prototype.fp_display_filelist = function (
      options,
      fileslist,
      lazyloading
    ) {
      var viewmodeclassnames = {
        1: "fp-iconview",
        2: "fp-treeview",
        3: "fp-tableview",
      };
      var classname = viewmodeclassnames[options.viewmode];
      var scope = this;
      var file_is_folder = function (node) {
        if (node.children) {
          return !0;
        }
        if (node.type && node.type == "folder") {
          return !0;
        }
        return !1;
      };
      var file_get_filename = function (node) {
        return node.title ? node.title : node.fullname;
      };
      var file_get_displayname = function (node) {
        var displayname = node.shorttitle
          ? node.shorttitle
          : file_get_filename(node);
        return Y.Escape.html(displayname);
      };
      var file_get_description = function (node) {
        var description = "";
        if (node.description) {
          description = node.description;
        } else if (node.thumbnail_title) {
          description = node.thumbnail_title;
        } else {
          description = file_get_filename(node);
        }
        return Y.Escape.html(description);
      };
      var build_tree = function (node, level) {
        var el = Y.Node.create("<div/>");
        el.appendChild(options.filenode.cloneNode(!0));
        el.one(".fp-filename").setContent(file_get_displayname(node));
        var tmpnodedata = { className: options.classnamecallback(node) };
        el.get("children").addClass(tmpnodedata.className);
        if (node.icon) {
          el.one(".fp-icon").appendChild(Y.Node.create("<img/>"));
          el.one(".fp-icon img").setImgSrc(
            node.icon,
            node.realicon,
            lazyloading
          );
        }
        tmpnodedata.html = el.getContent();
        var tmpNode = new Y.YUI2.widget.HTMLNode(tmpnodedata, level, !1);
        if (node.dynamicLoadComplete) {
          tmpNode.dynamicLoadComplete = !0;
        }
        tmpNode.fileinfo = node;
        tmpNode.isLeaf = !file_is_folder(node);
        if (!tmpNode.isLeaf) {
          if (node.expanded) {
            tmpNode.expand();
          }
          tmpNode.path = node.path
            ? node.path
            : node.filepath
            ? node.filepath
            : "";
          for (var c in node.children) {
            build_tree(node.children[c], tmpNode);
          }
        }
      };
      var initialize_tree_view = function () {
        var parentid = scope.one("." + classname).get("id");
        scope.treeview = new Y.YUI2.widget.TreeView(parentid);
        if (options.dynload) {
          scope.treeview.setDynamicLoad(
            Y.bind(options.treeview_dynload, options.callbackcontext),
            1
          );
        }
        scope.treeview.singleNodeHighlight = !0;
        if (options.filepath && options.filepath.length) {
          var mytree = {};
          var mytreeel = null;
          for (var i in options.filepath) {
            if (mytreeel == null) {
              mytreeel = mytree;
            } else {
              mytreeel.children = [{}];
              mytreeel = mytreeel.children[0];
            }
            var pathelement = options.filepath[i];
            mytreeel.path = pathelement.path;
            mytreeel.title = pathelement.name;
            mytreeel.icon = pathelement.icon;
            mytreeel.dynamicLoadComplete = !0;
            mytreeel.expanded = !0;
          }
          mytreeel.children = fileslist;
          build_tree(mytree, scope.treeview.getRoot());
          if (options.dynload) {
            var root = scope.treeview.getRoot();
            var isSearchResult =
              typeof options.callbackcontext.active_repo !== "undefined" &&
              options.callbackcontext.active_repo.issearchresult;
            while (root && root.children && root.children.length) {
              root = root.children[0];
              if (root.path == mytreeel.path) {
                root.origpath = options.filepath;
                root.origlist = fileslist;
              } else if (!root.isLeaf && root.expanded && !isSearchResult) {
                Y.bind(options.treeview_dynload, options.callbackcontext)(
                  root,
                  null
                );
              }
            }
          }
        } else {
          for (k in fileslist) {
            build_tree(fileslist[k], scope.treeview.getRoot());
          }
        }
        scope.treeview.subscribe("clickEvent", function (e) {
          e.node.highlight(!1);
          var callback = options.callback;
          if (
            options.rightclickcallback &&
            e.event.target &&
            Y.Node(e.event.target).ancestor(".fp-treeview .fp-contextmenu", !0)
          ) {
            callback = options.rightclickcallback;
          }
          Y.bind(callback, options.callbackcontext)(e, e.node.fileinfo);
          Y.YUI2.util.Event.stopEvent(e.event);
        });
        scope.treeview.subscribe("enterKeyPressed", function (node) {
          if (node.children.length === 0) {
            Y.one(node.getContentEl()).one("a").simulate("click");
          }
        });
        scope.treeview.draw();
      };
      var formatValue = function (o) {
        if (o.data["" + o.column.key + "_f_s"]) {
          return o.data["" + o.column.key + "_f_s"];
        } else if (o.data["" + o.column.key + "_f"]) {
          return o.data["" + o.column.key + "_f"];
        } else if (o.value) {
          return o.value;
        } else {
          return "";
        }
      };
      var formatTitle = function (o) {
        var el = Y.Node.create("<div/>");
        el.appendChild(options.filenode.cloneNode(!0));
        el.get("children").addClass(o.data.classname);
        el.one(".fp-filename").setContent(o.value);
        if (o.data.icon) {
          el.one(".fp-icon").appendChild(Y.Node.create("<img/>"));
          el.one(".fp-icon img").setImgSrc(
            o.data.icon,
            o.data.realicon,
            lazyloading
          );
        }
        if (options.rightclickcallback) {
          el.get("children").addClass("fp-hascontextmenu");
        }
        return el.getContent();
      };
      var formatCheckbox = function (o) {
        var el = Y.Node.create("<div/>");
        var checkbox = Y.Node.create("<input/>")
          .setAttribute("type", "checkbox")
          .setAttribute("data-fieldtype", "checkbox")
          .setAttribute("data-fullname", o.data.fullname)
          .setAttribute("data-action", "toggle")
          .setAttribute("data-toggle", "slave")
          .setAttribute("data-togglegroup", "file-selections")
          .setAttribute(
            "data-toggle-selectall",
            M.util.get_string("selectall", "moodle")
          )
          .setAttribute(
            "data-toggle-deselectall",
            M.util.get_string("deselectall", "moodle")
          );
        var checkboxLabel = Y.Node.create("<label>")
          .setHTML("Select file '" + o.data.fullname + "'")
          .addClass("sr-only")
          .setAttrs({ for: checkbox.generateID() });
        el.appendChild(checkbox);
        el.appendChild(checkboxLabel);
        return el.getContent();
      };
      var sortFoldersFirst = function (a, b, desc) {
        if (a.get("isfolder") && !b.get("isfolder")) {
          return -1;
        }
        if (!a.get("isfolder") && b.get("isfolder")) {
          return 1;
        }
        var aa = a.get(this.key),
          bb = b.get(this.key),
          dir = desc ? -1 : 1;
        return aa > bb ? dir : aa < bb ? -dir : 0;
      };
      var initialize_table_view = function () {
        var cols = [
          {
            key: "displayname",
            label: M.util.get_string("name", "moodle"),
            allowHTML: !0,
            formatter: formatTitle,
            sortable: !0,
            sortFn: sortFoldersFirst,
          },
          {
            key: "datemodified",
            label: M.util.get_string("lastmodified", "moodle"),
            allowHTML: !0,
            formatter: formatValue,
            sortable: !0,
            sortFn: sortFoldersFirst,
          },
          {
            key: "size",
            label: M.util.get_string("size", "repository"),
            allowHTML: !0,
            formatter: formatValue,
            sortable: !0,
            sortFn: sortFoldersFirst,
          },
          {
            key: "mimetype",
            label: M.util.get_string("type", "repository"),
            allowHTML: !0,
            sortable: !0,
            sortFn: sortFoldersFirst,
          },
        ];
        var div = Y.Node.create("<div/>");
        var checkbox = Y.Node.create("<input/>")
          .setAttribute("type", "checkbox")
          .setAttribute("data-action", "toggle")
          .setAttribute("data-toggle", "master")
          .setAttribute("data-togglegroup", "file-selections");
        var checkboxLabel = Y.Node.create("<label>")
          .setHTML(M.util.get_string("selectallornone", "form"))
          .addClass("sr-only")
          .setAttrs({ for: checkbox.generateID() });
        div.appendChild(checkboxLabel);
        div.appendChild(checkbox);
        var clickEventSelector = "tr";
        if (
          options.disablecheckboxes != undefined &&
          !options.disablecheckboxes
        ) {
          clickEventSelector = "tr td:not(:first-child)";
          cols.unshift({
            key: "",
            label: div.getContent(),
            allowHTML: !0,
            formatter: formatCheckbox,
            sortable: !1,
          });
        }
        scope.tableview = new Y.DataTable({ columns: cols, data: fileslist });
        scope.tableview.delegate(
          "click",
          function (e, tableview) {
            var record = tableview.getRecord(e.currentTarget.get("id"));
            if (record) {
              var callback = options.callback;
              if (
                options.rightclickcallback &&
                e.target.ancestor(".fp-tableview .fp-contextmenu", !0)
              ) {
                callback = options.rightclickcallback;
              }
              Y.bind(callback, this)(e, record.getAttrs());
            }
          },
          clickEventSelector,
          options.callbackcontext,
          scope.tableview
        );
        if (options.rightclickcallback) {
          scope.tableview.delegate(
            "contextmenu",
            function (e, tableview) {
              var record = tableview.getRecord(e.currentTarget.get("id"));
              if (record) {
                Y.bind(options.rightclickcallback, this)(e, record.getAttrs());
              }
            },
            "tr",
            options.callbackcontext,
            scope.tableview
          );
        }
      };
      var append_files_table = function () {
        if (options.appendonly) {
          fileslist.forEach(function (el) {
            this.tableview.data.add(el);
          }, scope);
        }
        scope.tableview.render(scope.one("." + classname));
        scope.tableview.sortable = options.sortable ? !0 : !1;
      };
      var append_files_tree = function () {
        if (options.appendonly) {
          var parentnode = scope.treeview.getRoot();
          if (scope.treeview.getHighlightedNode()) {
            parentnode = scope.treeview.getHighlightedNode();
            if (parentnode.isLeaf) {
              parentnode = parentnode.parent;
            }
          }
          for (var k in fileslist) {
            build_tree(fileslist[k], parentnode);
          }
          scope.treeview.draw();
        } else {
        }
      };
      var append_files_icons = function () {
        parent = scope.one("." + classname);
        for (var k in fileslist) {
          var node = fileslist[k];
          var element = options.filenode.cloneNode(!0);
          parent.appendChild(element);
          element.addClass(options.classnamecallback(node));
          var filenamediv = element.one(".fp-filename");
          filenamediv.setContent(file_get_displayname(node));
          var imgdiv = element.one(".fp-thumbnail"),
            width,
            height,
            src;
          if (node.thumbnail) {
            width = node.thumbnail_width ? node.thumbnail_width : 90;
            height = node.thumbnail_height ? node.thumbnail_height : 90;
            src = node.thumbnail;
          } else {
            width = 16;
            height = 16;
            src = node.icon;
          }
          filenamediv.setStyleAdv("width", width);
          imgdiv.setStyleAdv("width", width).setStyleAdv("height", height);
          var img = Y.Node.create("<img/>")
            .setAttrs({
              title: file_get_description(node),
              alt: Y.Escape.html(
                node.thumbnail_alt
                  ? node.thumbnail_alt
                  : file_get_filename(node)
              ),
            })
            .setStyle("maxWidth", "" + width + "px")
            .setStyle("maxHeight", "" + height + "px");
          img.setImgSrc(src, node.realthumbnail, lazyloading);
          imgdiv.appendChild(img);
          element.on(
            "click",
            function (e, nd) {
              if (
                options.rightclickcallback &&
                e.target.ancestor(".fp-iconview .fp-contextmenu", !0)
              ) {
                Y.bind(options.rightclickcallback, this)(e, nd);
              } else {
                Y.bind(options.callback, this)(e, nd);
              }
            },
            options.callbackcontext,
            node
          );
          if (options.rightclickcallback) {
            element.on(
              "contextmenu",
              options.rightclickcallback,
              options.callbackcontext,
              node
            );
          }
        }
      };
      var problemFiles = [];
      fileslist.forEach(function (file) {
        if (
          !file_is_folder(file) &&
          file.hasOwnProperty("status") &&
          file.status != 0
        ) {
          problemFiles.push(file);
        }
      });
      if (problemFiles.length > 0) {
        require(["core/notification", "core/str"], function (
          Notification,
          Str
        ) {
          problemFiles.forEach(function (problemFile) {
            Str.get_string(
              "storedfilecannotreadfile",
              "error",
              problemFile.fullname
            )
              .then(function (string) {
                Notification.addNotification({
                  message: string,
                  type: "error",
                });
                return;
              })
              .catch(Notification.exception);
          });
        });
      }
      if (options.viewmode == 3) {
        fileslist.forEach(function (el) {
          el.displayname = file_get_displayname(el);
          el.isfolder = file_is_folder(el);
          el.classname = options.classnamecallback(el);
        }, scope);
      }
      if (!options.appendonly) {
        var parent = Y.Node.create("<div/>").addClass(classname);
        this.setContent("").appendChild(parent);
        parent.generateID();
        if (options.viewmode == 2) {
          initialize_tree_view();
        } else if (options.viewmode == 3) {
          initialize_table_view();
        } else {
        }
      }
      if (options.viewmode == 2) {
        append_files_tree();
      } else if (options.viewmode == 3) {
        append_files_table();
      } else {
        append_files_icons();
      }
    };
  },
  "@VERSION@",
  {
    requires: [
      "base",
      "node",
      "yui2-treeview",
      "panel",
      "cookie",
      "datatable",
      "datatable-sort",
    ],
  }
);
M.core_filepicker = M.core_filepicker || {};
M.core_filepicker.instances = M.core_filepicker.instances || {};
M.core_filepicker.active_filepicker = null;
M.core_filepicker.templates = M.core_filepicker.templates || {};
M.core_filepicker.loadedpreviews = M.core_filepicker.loadedpreviews || {};
M.core_filepicker.select_file = function (file) {
  M.core_filepicker.active_filepicker.select_file(file);
};
M.core_filepicker.show = function (Y, options) {
  if (!M.core_filepicker.instances[options.client_id]) {
    M.core_filepicker.init(Y, options);
  }
  M.core_filepicker.instances[options.client_id].options.formcallback =
    options.formcallback;
  M.core_filepicker.instances[options.client_id].show();
};
M.core_filepicker.set_templates = function (Y, templates) {
  for (var templid in templates) {
    M.core_filepicker.templates[templid] = templates[templid];
  }
};
M.core_filepicker.init = function (Y, options) {
  var FilePickerHelper = function (options) {
    FilePickerHelper.superclass.constructor.apply(this, arguments);
  };
  FilePickerHelper.NAME = "FilePickerHelper";
  FilePickerHelper.ATTRS = { options: {}, lang: {} };
  Y.extend(FilePickerHelper, Y.Base, {
    api: M.cfg.wwwroot + "/repository/repository_ajax.php",
    cached_responses: {},
    waitinterval: null,
    initializer: function (options) {
      this.options = options;
      if (!this.options.savepath) {
        this.options.savepath = "/";
      }
    },
    destructor: function () {},
    request: function (args, redraw) {
      var api = (args.api ? args.api : this.api) + "?action=" + args.action;
      var params = {};
      var scope = args.scope ? args.scope : this;
      params.repo_id = args.repository_id;
      params.p = args.path ? args.path : "";
      params.page = args.page ? args.page : "";
      params.env = this.options.env;
      params.accepted_types = this.options.accepted_types;
      params.sesskey = M.cfg.sesskey;
      params.client_id = args.client_id;
      params.itemid = this.options.itemid ? this.options.itemid : 0;
      params.maxbytes = this.options.maxbytes ? this.options.maxbytes : -1;
      params.areamaxbytes = this.options.areamaxbytes
        ? this.options.areamaxbytes
        : -1;
      if (this.options.context && this.options.context.id) {
        params.ctx_id = this.options.context.id;
      }
      if (args.params) {
        for (i in args.params) {
          params[i] = args.params[i];
        }
      }
      if (args.action == "upload") {
        var list = [];
        for (var k in params) {
          var value = params[k];
          if (value instanceof Array) {
            for (var i in value) {
              list.push(k + "[]=" + value[i]);
            }
          } else {
            list.push(k + "=" + value);
          }
        }
        params = list.join("&");
      } else {
        params = build_querystring(params);
      }
      var cfg = {
        method: "POST",
        on: {
          complete: function (id, o, p) {
            var data = null;
            try {
              data = Y.JSON.parse(o.responseText);
            } catch (e) {
              if (o && o.status && o.status > 0) {
                Y.use("moodle-core-notification-exception", function () {
                  return new M.core.exception(e);
                });
                return;
              }
            }
            if (data && data.error) {
              Y.use("moodle-core-notification-ajaxexception", function () {
                return new M.core.ajaxException(data);
              });
              this.fpnode.one(".fp-content").setContent("");
              return;
            } else {
              if (data.msg) {
                scope.print_msg(data.msg, "info");
              }
              if (args.action != "upload" && data.allowcaching) {
                scope.cached_responses[params] = data;
              }
              args.callback(id, data, p);
            }
          },
        },
        arguments: { scope: scope },
        headers: {
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        data: params,
        context: this,
      };
      if (args.form) {
        cfg.form = args.form;
      }
      if (
        !args.form &&
        args.action != "upload" &&
        scope.cached_responses[params]
      ) {
        args.callback(null, scope.cached_responses[params], { scope: scope });
      } else {
        Y.io(api, cfg);
        if (redraw) {
          this.wait();
        }
      }
    },
    process_existing_file: function (data) {
      var scope = this;
      var handleOverwrite = function (e) {
        e.preventDefault();
        var data = this.process_dlg.dialogdata;
        var params = {};
        params.existingfilename = data.existingfile.filename;
        params.existingfilepath = data.existingfile.filepath;
        params.newfilename = data.newfile.filename;
        params.newfilepath = data.newfile.filepath;
        this.hide_header();
        this.request(
          {
            params: params,
            scope: this,
            action: "overwrite",
            path: "",
            client_id: this.options.client_id,
            repository_id: this.active_repo.id,
            callback: function (id, o, args) {
              scope.hide();
              var urlimage =
                data.existingfile.url + "?time=" + new Date().getTime();
              if (
                scope.options.editor_target &&
                scope.options.env == "editor"
              ) {
                scope.options.editor_target.value = urlimage;
                scope.options.editor_target.dispatchEvent(new Event("change"), {
                  bubbles: !0,
                });
              }
              var fileinfo = {
                client_id: scope.options.client_id,
                url: urlimage,
                file: data.existingfile.filename,
              };
              var formcallback_scope = scope.options.magicscope
                ? scope.options.magicscope
                : scope;
              scope.options.formcallback.apply(formcallback_scope, [fileinfo]);
            },
          },
          !0
        );
      };
      var handleRename = function (e) {
        e.preventDefault();
        var scope = this;
        var data = this.process_dlg.dialogdata;
        if (scope.options.editor_target && scope.options.env == "editor") {
          scope.options.editor_target.value = data.newfile.url;
          scope.options.editor_target.dispatchEvent(new Event("change"), {
            bubbles: !0,
          });
        }
        scope.hide();
        var formcallback_scope = scope.options.magicscope
          ? scope.options.magicscope
          : scope;
        var fileinfo = {
          client_id: scope.options.client_id,
          url: data.newfile.url,
          file: data.newfile.filename,
        };
        scope.options.formcallback.apply(formcallback_scope, [fileinfo]);
      };
      var handleCancel = function (e) {
        e.preventDefault();
        var params = {};
        params.newfilename = this.process_dlg.dialogdata.newfile.filename;
        params.newfilepath = this.process_dlg.dialogdata.newfile.filepath;
        this.request(
          {
            params: params,
            scope: this,
            action: "deletetmpfile",
            path: "",
            client_id: this.options.client_id,
            repository_id: this.active_repo.id,
            callback: function (id, o, args) {},
          },
          !1
        );
        this.process_dlg.hide();
        this.selectui.hide();
      };
      if (!this.process_dlg) {
        this.process_dlg_node = Y.Node.create(
          M.core_filepicker.templates.processexistingfile
        );
        var node = this.process_dlg_node;
        node.generateID();
        this.process_dlg = new M.core.dialogue({
          draggable: !0,
          bodyContent: node,
          headerContent: M.util.get_string(
            "fileexistsdialogheader",
            "repository"
          ),
          centered: !0,
          modal: !0,
          visible: !1,
          zIndex: this.options.zIndex,
        });
        node.one(".fp-dlg-butoverwrite").on("click", handleOverwrite, this);
        node.one(".fp-dlg-butrename").on("click", handleRename, this);
        node.one(".fp-dlg-butcancel").on("click", handleCancel, this);
        if (this.options.env == "editor") {
          node
            .one(".fp-dlg-text")
            .setContent(
              M.util.get_string("fileexistsdialog_editor", "repository")
            );
        } else {
          node
            .one(".fp-dlg-text")
            .setContent(
              M.util.get_string("fileexistsdialog_filemanager", "repository")
            );
        }
      }
      this.selectnode.removeClass("loading");
      this.process_dlg.dialogdata = data;
      this.process_dlg_node
        .one(".fp-dlg-butrename")
        .setContent(
          M.util.get_string("renameto", "repository", data.newfile.filename)
        );
      this.process_dlg.show();
    },
    display_error: function (errortext, errorcode) {
      this.fpnode
        .one(".fp-content")
        .setContent(M.core_filepicker.templates.error);
      this.fpnode
        .one(".fp-content .fp-error")
        .addClass(errorcode)
        .setContent(Y.Escape.html(errortext));
    },
    print_msg: function (msg, type) {
      var header = M.util.get_string("error", "moodle");
      if (type != "error") {
        type = "info";
        header = M.util.get_string("info", "moodle");
      }
      if (!this.msg_dlg) {
        this.msg_dlg_node = Y.Node.create(M.core_filepicker.templates.message);
        this.msg_dlg_node.generateID();
        this.msg_dlg = new M.core.dialogue({
          draggable: !0,
          bodyContent: this.msg_dlg_node,
          centered: !0,
          modal: !0,
          visible: !1,
          zIndex: this.options.zIndex,
        });
        this.msg_dlg_node.one(".fp-msg-butok").on(
          "click",
          function (e) {
            e.preventDefault();
            this.msg_dlg.hide();
          },
          this
        );
      }
      this.msg_dlg.set("headerContent", header);
      this.msg_dlg_node
        .removeClass("fp-msg-info")
        .removeClass("fp-msg-error")
        .addClass("fp-msg-" + type);
      this.msg_dlg_node.one(".fp-msg-text").setContent(Y.Escape.html(msg));
      this.msg_dlg.show();
    },
    view_files: function (appenditems) {
      this.viewbar_set_enabled(!0);
      this.print_path();
      if (this.viewmode == 2) {
        this.view_as_list(appenditems);
      } else if (this.viewmode == 3) {
        this.view_as_table(appenditems);
      } else {
        this.view_as_icons(appenditems);
      }
      this.fpnode.one(".fp-content").setAttribute("tabindex", "0");
      this.fpnode.one(".fp-content").focus();
      if (!appenditems && this.active_repo.hasmorepages) {
        if (!this.fpnode.one(".fp-content .fp-nextpage")) {
          this.fpnode
            .one(".fp-content")
            .append(M.core_filepicker.templates.nextpage);
        }
        this.fpnode
          .one(".fp-content .fp-nextpage")
          .one("a,button")
          .on(
            "click",
            function (e) {
              e.preventDefault();
              this.fpnode.one(".fp-content .fp-nextpage").addClass("loading");
              this.request_next_page();
            },
            this
          );
      }
      if (
        !this.active_repo.hasmorepages &&
        this.fpnode.one(".fp-content .fp-nextpage")
      ) {
        this.fpnode.one(".fp-content .fp-nextpage").remove();
      }
      if (this.fpnode.one(".fp-content .fp-nextpage")) {
        this.fpnode.one(".fp-content .fp-nextpage").removeClass("loading");
      }
      this.content_scrolled();
    },
    content_scrolled: function (e) {
      setTimeout(
        Y.bind(function () {
          if (this.processingimages) {
            return;
          }
          this.processingimages = !0;
          var scope = this,
            fpcontent = this.fpnode.one(".fp-content"),
            fpcontenty = fpcontent.getY(),
            fpcontentheight = fpcontent.getStylePx("height"),
            nextpage = fpcontent.one(".fp-nextpage"),
            is_node_visible = function (node) {
              var offset = node.getY() - fpcontenty;
              if (
                offset <= fpcontentheight &&
                (offset >= 0 || offset + node.getStylePx("height") >= 0)
              ) {
                return !0;
              }
              return !1;
            };
          if (
            nextpage &&
            !nextpage.hasClass("loading") &&
            is_node_visible(nextpage)
          ) {
            nextpage.one("a,button").simulate("click");
          }
          if (scope.lazyloading) {
            fpcontent.all("img").each(function (node) {
              if (
                node.get("id") &&
                scope.lazyloading[node.get("id")] &&
                is_node_visible(node)
              ) {
                node.setImgRealSrc(scope.lazyloading);
              }
            });
          }
          this.processingimages = !1;
        }, this),
        200
      );
    },
    treeview_dynload: function (node, cb) {
      var retrieved_children = {};
      if (node.children) {
        for (var i in node.children) {
          retrieved_children[node.children[i].path] = node.children[i];
        }
      }
      this.request(
        {
          action: "list",
          client_id: this.options.client_id,
          repository_id: this.active_repo.id,
          path: node.path ? node.path : "",
          page: node.page ? args.page : "",
          scope: this,
          callback: function (id, obj, args) {
            var list = obj.list;
            var scope = args.scope;
            if (
              !(
                scope.active_repo.id == obj.repo_id &&
                scope.viewmode == 2 &&
                node &&
                node.getChildrenEl()
              )
            ) {
              return;
            }
            if (cb != null) {
              scope.viewbar_set_enabled(!0);
              scope.parse_repository_options(obj);
            }
            node.highlight(!1);
            node.origlist = obj.list ? obj.list : null;
            node.origpath = obj.path ? obj.path : null;
            node.children = [];
            for (k in list) {
              if (list[k].children && retrieved_children[list[k].path]) {
                node.children[node.children.length] =
                  retrieved_children[list[k].path];
              } else {
                scope.view_as_list([list[k]]);
              }
            }
            if (cb == null) {
              node.refresh();
            } else {
              cb();
            }
            scope.content_scrolled();
          },
        },
        !1
      );
    },
    classnamecallback: function (node) {
      var classname = "";
      if (node.children) {
        classname = classname + " fp-folder";
      }
      if (node.isref) {
        classname = classname + " fp-isreference";
      }
      if (node.iscontrolledlink) {
        classname = classname + " fp-iscontrolledlink";
      }
      if (node.refcount) {
        classname = classname + " fp-hasreferences";
      }
      if (node.originalmissing) {
        classname = classname + " fp-originalmissing";
      }
      return Y.Lang.trim(classname);
    },
    view_as_list: function (appenditems) {
      var list = appenditems != null ? appenditems : this.filelist;
      this.viewmode = 2;
      if (
        !this.filelist ||
        (this.filelist.length == 0 && (!this.filepath || !this.filepath.length))
      ) {
        this.display_error(
          M.util.get_string("nofilesavailable", "repository"),
          "nofilesavailable"
        );
        return;
      }
      var element_template = Y.Node.create(
        M.core_filepicker.templates.listfilename
      );
      var options = {
        viewmode: this.viewmode,
        appendonly: appenditems != null,
        filenode: element_template,
        callbackcontext: this,
        callback: function (e, node) {
          if (!node.children) {
            if (e.node.parent && e.node.parent.origpath) {
              this.filepath = e.node.parent.origpath;
              this.filelist = e.node.parent.origlist;
              this.print_path();
            }
            this.select_file(node);
          } else {
            this.filepath = e.node.origpath;
            this.filelist = e.node.origlist;
            this.currentpath = e.node.path;
            this.print_path();
            this.content_scrolled();
          }
        },
        classnamecallback: this.classnamecallback,
        dynload: this.active_repo.dynload,
        filepath: this.filepath,
        treeview_dynload: this.treeview_dynload,
      };
      this.fpnode
        .one(".fp-content")
        .fp_display_filelist(options, list, this.lazyloading);
    },
    view_as_icons: function (appenditems) {
      this.viewmode = 1;
      var list = appenditems != null ? appenditems : this.filelist;
      var element_template = Y.Node.create(
        M.core_filepicker.templates.iconfilename
      );
      if (appenditems == null && (!this.filelist || !this.filelist.length)) {
        this.display_error(
          M.util.get_string("nofilesavailable", "repository"),
          "nofilesavailable"
        );
        return;
      }
      var options = {
        viewmode: this.viewmode,
        appendonly: appenditems != null,
        filenode: element_template,
        callbackcontext: this,
        callback: function (e, node) {
          if (e.preventDefault) {
            e.preventDefault();
          }
          if (node.children) {
            if (this.active_repo.dynload) {
              this.list({ path: node.path });
            } else {
              this.filelist = node.children;
              this.view_files();
            }
          } else {
            this.select_file(node);
          }
        },
        classnamecallback: this.classnamecallback,
      };
      this.fpnode
        .one(".fp-content")
        .fp_display_filelist(options, list, this.lazyloading);
    },
    view_as_table: function (appenditems) {
      this.viewmode = 3;
      var list = appenditems != null ? appenditems : this.filelist;
      if (
        !appenditems &&
        (!this.filelist || this.filelist.length == 0) &&
        !this.active_repo.hasmorepages
      ) {
        this.display_error(
          M.util.get_string("nofilesavailable", "repository"),
          "nofilesavailable"
        );
        return;
      }
      var element_template = Y.Node.create(
        M.core_filepicker.templates.listfilename
      );
      var options = {
        viewmode: this.viewmode,
        appendonly: appenditems != null,
        filenode: element_template,
        callbackcontext: this,
        sortable: !this.active_repo.hasmorepages,
        callback: function (e, node) {
          if (e.preventDefault) {
            e.preventDefault();
          }
          if (node.children) {
            if (this.active_repo.dynload) {
              this.list({ path: node.path });
            } else {
              this.filelist = node.children;
              this.view_files();
            }
          } else {
            this.select_file(node);
          }
        },
        classnamecallback: this.classnamecallback,
      };
      this.fpnode
        .one(".fp-content")
        .fp_display_filelist(options, list, this.lazyloading);
    },
    request_next_page: function () {
      if (
        !this.active_repo.hasmorepages ||
        this.active_repo.nextpagerequested
      ) {
        return;
      }
      this.active_repo.nextpagerequested = !0;
      var nextpage = this.active_repo.page + 1;
      var args = { page: nextpage, repo_id: this.active_repo.id };
      var action = this.active_repo.issearchresult ? "search" : "list";
      this.request(
        {
          path: this.currentpath,
          scope: this,
          action: action,
          client_id: this.options.client_id,
          repository_id: args.repo_id,
          params: args,
          callback: function (id, obj, args) {
            var scope = args.scope;
            var samepage = !0;
            if (obj.path && scope.filepath) {
              var pathbefore = scope.filepath[scope.filepath.length - 1];
              var pathafter = obj.path[obj.path.length - 1];
              if (pathbefore.path != pathafter.path) {
                samepage = !1;
              }
            }
            if (
              scope.active_repo.hasmorepages &&
              obj.list &&
              obj.page &&
              obj.repo_id == scope.active_repo.id &&
              obj.page == scope.active_repo.page + 1 &&
              samepage
            ) {
              scope.parse_repository_options(obj, !0);
              scope.view_files(obj.list);
            }
          },
        },
        !1
      );
    },
    select_file: function (args) {
      var argstitle = args.shorttitle ? args.shorttitle : args.title;
      var titlelength = 30;
      if (argstitle.length > titlelength) {
        argstitle = argstitle.substring(0, titlelength) + "...";
      }
      Y.one("#fp-file_label_" + this.options.client_id).setContent(
        Y.Escape.html(
          M.util.get_string("select", "repository") + " " + argstitle
        )
      );
      this.selectui.show();
      Y.one("#" + this.selectnode.get("id")).focus();
      var client_id = this.options.client_id;
      var selectnode = this.selectnode;
      var return_types =
        this.options.repositories[this.active_repo.id].return_types;
      selectnode.removeClass("loading");
      selectnode.one(".fp-saveas input").set("value", args.title);
      var imgnode = Y.Node.create("<img/>")
        .set("src", args.realthumbnail ? args.realthumbnail : args.thumbnail)
        .setStyle(
          "maxHeight",
          "" + (args.thumbnail_height ? args.thumbnail_height : 90) + "px"
        )
        .setStyle(
          "maxWidth",
          "" + (args.thumbnail_width ? args.thumbnail_width : 90) + "px"
        );
      selectnode.one(".fp-thumbnail").setContent("").appendChild(imgnode);
      var filelinktypes = [2, 1, 4, 8];
      var filelink = {},
        firstfilelink = null,
        filelinkcount = 0;
      for (var i in filelinktypes) {
        var allowed =
          return_types & filelinktypes[i] &&
          this.options.return_types & filelinktypes[i];
        if (
          filelinktypes[i] == 1 &&
          !this.options.externallink &&
          this.options.env == "editor"
        ) {
          allowed = !1;
        }
        filelink[filelinktypes[i]] = allowed;
        firstfilelink =
          firstfilelink == null && allowed ? filelinktypes[i] : firstfilelink;
        filelinkcount += allowed ? 1 : 0;
      }
      var defaultreturntype =
        this.options.repositories[this.active_repo.id].defaultreturntype;
      if (defaultreturntype) {
        if (filelink[defaultreturntype]) {
          firstfilelink = defaultreturntype;
        }
      }
      for (var linktype in filelink) {
        var el = selectnode.one(".fp-linktype-" + linktype);
        el.addClassIf("uneditable", !(filelink[linktype] && filelinkcount > 1));
        el.one("input")
          .set("checked", firstfilelink == linktype ? "checked" : "")
          .simulate("change");
      }
      selectnode
        .one(".fp-setauthor input")
        .set("value", args.author ? args.author : this.options.author);
      this.populateLicensesSelect(
        selectnode.one(".fp-setlicense select"),
        args
      );
      selectnode.one("form #filesource-" + client_id).set("value", args.source);
      selectnode
        .one("form #filesourcekey-" + client_id)
        .set("value", args.sourcekey);
      var attrs = [
        "datemodified",
        "datecreated",
        "size",
        "license",
        "author",
        "dimensions",
      ];
      for (var i in attrs) {
        if (selectnode.one(".fp-" + attrs[i])) {
          var value = args[attrs[i] + "_f"]
            ? args[attrs[i] + "_f"]
            : args[attrs[i]]
            ? args[attrs[i]]
            : "";
          selectnode
            .one(".fp-" + attrs[i])
            .addClassIf("fp-unknown", "" + value == "")
            .one(".fp-value")
            .setContent(Y.Escape.html(value));
        }
      }
    },
    setup_select_file: function () {
      var client_id = this.options.client_id;
      var selectnode = this.selectnode;
      var getfile = selectnode.one(".fp-select-confirm");
      var filePickerHelper = this;
      selectnode
        .all(
          ".fp-saveas,.fp-linktype-2,.fp-linktype-1,.fp-linktype-4,fp-linktype-8,.fp-setauthor,.fp-setlicense"
        )
        .each(function (node) {
          node.all("label").set("for", node.one("input,select").generateID());
        });
      selectnode
        .one(".fp-linktype-2 input")
        .setAttrs({ value: 2, name: "linktype" });
      selectnode
        .one(".fp-linktype-1 input")
        .setAttrs({ value: 1, name: "linktype" });
      selectnode
        .one(".fp-linktype-4 input")
        .setAttrs({ value: 4, name: "linktype" });
      selectnode
        .one(".fp-linktype-8 input")
        .setAttrs({ value: 8, name: "linktype" });
      var changelinktype = function (e) {
        if (e.currentTarget.get("checked")) {
          var allowinputs = e.currentTarget.get("value") != 1;
          selectnode
            .all(".fp-setauthor,.fp-setlicense,.fp-saveas")
            .each(function (node) {
              node.addClassIf("uneditable", !allowinputs);
              node
                .all("input,select")
                .set("disabled", allowinputs ? "" : "disabled");
            });
          if (e.currentTarget.get("value") === "4") {
            var filereferencewarning =
              filePickerHelper.active_repo.filereferencewarning;
            if (filereferencewarning) {
              var fileReferenceNode =
                e.currentTarget.ancestor(".fp-linktype-4");
              var fileReferenceWarningNode = Y.Node.create("<div/>")
                .addClass("alert alert-warning px-3 py-1 my-1 small")
                .setAttrs({ role: "alert" })
                .setContent(filereferencewarning);
              fileReferenceNode.append(fileReferenceWarningNode);
            }
          } else {
            var fileReferenceInput = selectnode.one(".fp-linktype-4 input");
            var fileReferenceWarningNode = fileReferenceInput
              .ancestor(".fp-linktype-4")
              .one(".alert-warning");
            if (fileReferenceWarningNode) {
              fileReferenceWarningNode.remove();
            }
          }
        }
      };
      selectnode
        .all(".fp-linktype-2,.fp-linktype-1,.fp-linktype-4,.fp-linktype-8")
        .each(function (node) {
          node.one("input").on("change", changelinktype, this);
        });
      getfile.on(
        "click",
        function (e) {
          e.preventDefault();
          var client_id = this.options.client_id;
          var scope = this;
          var repository_id = this.active_repo.id;
          var title = selectnode.one(".fp-saveas input").get("value");
          var filesource = selectnode
            .one("form #filesource-" + client_id)
            .get("value");
          var filesourcekey = selectnode
            .one("form #filesourcekey-" + client_id)
            .get("value");
          var params = {
            title: title,
            source: filesource,
            savepath: this.options.savepath,
            sourcekey: filesourcekey,
          };
          var license = selectnode.one(".fp-setlicense select");
          if (license) {
            params.license = license.get("value");
            var origlicense = selectnode.one(".fp-license .fp-value");
            if (origlicense) {
              origlicense = origlicense.getContent();
            }
            if (this.options.rememberuserlicensepref) {
              this.set_preference("recentlicense", license.get("value"));
            }
          }
          params.author = selectnode.one(".fp-setauthor input").get("value");
          var return_types =
            this.options.repositories[this.active_repo.id].return_types;
          if (this.options.env == "editor") {
            params.savepath = "/";
          }
          if (
            (this.options.externallink || this.options.env != "editor") &&
            return_types & 1 &&
            this.options.return_types & 1 &&
            selectnode.one(".fp-linktype-1 input").get("checked")
          ) {
            params.linkexternal = "yes";
          } else if (
            return_types & 4 &&
            this.options.return_types & 4 &&
            selectnode.one(".fp-linktype-4 input").get("checked")
          ) {
            params.usefilereference = "1";
          } else if (
            return_types & 8 &&
            this.options.return_types & 8 &&
            selectnode.one(".fp-linktype-8 input").get("checked")
          ) {
            params.usecontrolledlink = "1";
          }
          selectnode.addClass("loading");
          this.request(
            {
              action: "download",
              client_id: client_id,
              repository_id: repository_id,
              params: params,
              onerror: function (id, obj, args) {
                selectnode.removeClass("loading");
                scope.selectui.hide();
              },
              callback: function (id, obj, args) {
                selectnode.removeClass("loading");
                if (obj.event == "fileexists") {
                  scope.process_existing_file(obj);
                  return;
                }
                if (
                  scope.options.editor_target &&
                  scope.options.env == "editor"
                ) {
                  scope.options.editor_target.value = obj.url;
                  scope.options.editor_target.dispatchEvent(
                    new Event("change"),
                    { bubbles: !0 }
                  );
                }
                scope.hide();
                obj.client_id = client_id;
                var formcallback_scope = args.scope.options.magicscope
                  ? args.scope.options.magicscope
                  : args.scope;
                scope.options.formcallback.apply(formcallback_scope, [obj]);
              },
            },
            !1
          );
        },
        this
      );
      var elform = selectnode.one("form");
      elform.appendChild(
        Y.Node.create("<input/>").setAttrs({
          type: "hidden",
          id: "filesource-" + client_id,
        })
      );
      elform.appendChild(
        Y.Node.create("<input/>").setAttrs({
          type: "hidden",
          id: "filesourcekey-" + client_id,
        })
      );
      elform.on(
        "keydown",
        function (e) {
          if (e.keyCode == 13) {
            getfile.simulate("click");
            e.preventDefault();
          }
        },
        this
      );
      var cancel = selectnode.one(".fp-select-cancel");
      cancel.on(
        "click",
        function (e) {
          e.preventDefault();
          this.selectui.hide();
        },
        this
      );
    },
    wait: function () {
      if (this.waitinterval != null) {
        clearInterval(this.waitinterval);
      }
      var root = this.fpnode.one(".fp-content");
      var content = Y.Node.create(M.core_filepicker.templates.loading)
        .addClass("fp-content-hidden")
        .setStyle("opacity", 0);
      var count = 0;
      var interval = setInterval(function () {
        if (!content || !root.contains(content) || count >= 15) {
          clearInterval(interval);
          return !0;
        }
        if (count == 5) {
          content.removeClass("fp-content-hidden");
        } else if (count > 5) {
          var opacity = parseFloat(content.getStyle("opacity"));
          content.setStyle("opacity", opacity + 0.1);
        }
        count++;
        return !1;
      }, 100);
      this.waitinterval = interval;
      root.setContent(content);
    },
    viewbar_set_enabled: function (mode) {
      var viewbar = this.fpnode.one(".fp-viewbar");
      if (viewbar) {
        if (mode) {
          viewbar.addClass("enabled").removeClass("disabled");
          this.fpnode
            .all(".fp-vb-icons,.fp-vb-tree,.fp-vb-details")
            .setAttribute("aria-disabled", "false");
          this.fpnode
            .all(".fp-vb-icons,.fp-vb-tree,.fp-vb-details")
            .setAttribute("tabindex", "");
        } else {
          viewbar.removeClass("enabled").addClass("disabled");
          this.fpnode
            .all(".fp-vb-icons,.fp-vb-tree,.fp-vb-details")
            .setAttribute("aria-disabled", "true");
          this.fpnode
            .all(".fp-vb-icons,.fp-vb-tree,.fp-vb-details")
            .setAttribute("tabindex", "-1");
        }
      }
      this.fpnode
        .all(".fp-vb-icons,.fp-vb-tree,.fp-vb-details")
        .removeClass("checked");
      var modes = { 1: "icons", 2: "tree", 3: "details" };
      this.fpnode.all(".fp-vb-" + modes[this.viewmode]).addClass("checked");
    },
    viewbar_clicked: function (e) {
      e.preventDefault();
      var viewbar = this.fpnode.one(".fp-viewbar");
      if (!viewbar || !viewbar.hasClass("disabled")) {
        if (e.currentTarget.hasClass("fp-vb-tree")) {
          this.viewmode = 2;
        } else if (e.currentTarget.hasClass("fp-vb-details")) {
          this.viewmode = 3;
        } else {
          this.viewmode = 1;
        }
        this.viewbar_set_enabled(!0);
        this.view_files();
        this.set_preference("recentviewmode", this.viewmode);
      }
    },
    render: function () {
      var client_id = this.options.client_id;
      var fpid = "filepicker-" + client_id;
      var labelid = "fp-dialog-label_" + client_id;
      var width = 873;
      var draggable = !0;
      this.fpnode = Y.Node.create(M.core_filepicker.templates.generallayout)
        .set("id", "filepicker-" + client_id)
        .set("aria-labelledby", labelid);
      if (this.in_iframe()) {
        width = Math.floor(window.innerWidth * 0.95);
        draggable = !1;
      }
      this.mainui = new M.core.dialogue({
        extraClasses: ["filepicker"],
        draggable: draggable,
        bodyContent: this.fpnode,
        headerContent:
          '<h3 id="' +
          labelid +
          '">' +
          M.util.get_string("filepicker", "repository") +
          "</h3>",
        centered: !0,
        modal: !0,
        visible: !1,
        width: width + "px",
        responsiveWidth: 768,
        height: "558px",
        zIndex: this.options.zIndex,
        focusOnPreviousTargetAfterHide: !0,
        focusAfterHide: this.options.previousActiveElement,
      });
      this.selectnode = Y.Node.create(M.core_filepicker.templates.selectlayout)
        .set("id", "filepicker-select-" + client_id)
        .set("aria-live", "assertive")
        .set("role", "dialog");
      var fplabel = "fp-file_label_" + client_id;
      this.selectui = new M.core.dialogue({
        headerContent:
          '<h3 id="' +
          fplabel +
          '">' +
          M.util.get_string("select", "repository") +
          "</h3>",
        draggable: !0,
        width: "450px",
        bodyContent: this.selectnode,
        centered: !0,
        modal: !0,
        visible: !1,
        zIndex: this.options.zIndex,
      });
      Y.one("#" + this.selectnode.get("id")).setAttribute(
        "aria-labelledby",
        fplabel
      );
      this.fpnode
        .one(".fp-content")
        .on(["scroll", "resize"], this.content_scrolled, this);
      if (this.fpnode.one(".fp-path-folder")) {
        this.pathnode = this.fpnode.one(".fp-path-folder");
        this.pathbar = this.pathnode.get("parentNode");
        this.pathbar.removeChild(this.pathnode);
      }
      this.fpnode.one(".fp-vb-icons").on("click", this.viewbar_clicked, this);
      this.fpnode.one(".fp-vb-tree").on("click", this.viewbar_clicked, this);
      this.fpnode.one(".fp-vb-details").on("click", this.viewbar_clicked, this);
      this.setup_toolbar();
      this.setup_select_file();
      this.hide_header();
      var sorted_repositories = [];
      var i;
      for (i in this.options.repositories) {
        sorted_repositories[i] = this.options.repositories[i];
      }
      sorted_repositories.sort(function (a, b) {
        return a.sortorder - b.sortorder;
      });
      var reponode = this.fpnode.one(".fp-repo");
      if (reponode) {
        var list = reponode.get("parentNode");
        list.removeChild(reponode);
        for (i in sorted_repositories) {
          var repository = sorted_repositories[i];
          var h = parseInt(i) == 0 ? parseInt(i) : parseInt(i) - 1,
            j =
              parseInt(i) == Object.keys(sorted_repositories).length - 1
                ? parseInt(i)
                : parseInt(i) + 1;
          var previousrepository = sorted_repositories[h];
          var nextrepository = sorted_repositories[j];
          var node = reponode.cloneNode(!0);
          list.appendChild(node);
          node.set("id", "fp-repo-" + client_id + "-" + repository.id).on(
            "click",
            function (e, repository_id) {
              e.preventDefault();
              this.set_preference("recentrepository", repository_id);
              this.hide_header();
              this.list({ repo_id: repository_id });
            },
            this,
            repository.id
          );
          node.on(
            "key",
            function (
              e,
              previousrepositoryid,
              nextrepositoryid,
              clientid,
              repositoryid
            ) {
              this.changeHighlightedRepository(
                e,
                clientid,
                repositoryid,
                previousrepositoryid,
                nextrepositoryid
              );
            },
            "down:38,40",
            this,
            previousrepository.id,
            nextrepository.id,
            client_id,
            repository.id
          );
          node.on(
            "key",
            function (e, repositoryid) {
              e.preventDefault();
              this.set_preference("recentrepository", repositoryid);
              this.hide_header();
              this.list({ repo_id: repositoryid });
            },
            "enter",
            this,
            repository.id
          );
          node.one(".fp-repo-name").setContent(Y.Escape.html(repository.name));
          node.one(".fp-repo-icon").set("src", repository.icon);
          if (i == 0) {
            node.addClass("first");
          }
          if (i == sorted_repositories.length - 1) {
            node.addClass("last");
          }
          if (i % 2) {
            node.addClass("even");
          } else {
            node.addClass("odd");
          }
        }
      }
      if (sorted_repositories.length == 0) {
        this.display_error(
          M.util.get_string("norepositoriesavailable", "repository"),
          "norepositoriesavailable"
        );
      }
      this.mainui.show();
      this.show_recent_repository();
    },
    changeHighlightedRepository: function (
      event,
      clientid,
      oldrepositoryid,
      previousrepositoryid,
      nextrepositoryid
    ) {
      event.preventDefault();
      var newrepositoryid =
        event.keyCode == "40" ? nextrepositoryid : previousrepositoryid;
      this.fpnode
        .one("#fp-repo-" + clientid + "-" + oldrepositoryid)
        .setAttribute("tabindex", "-1");
      this.fpnode
        .one("#fp-repo-" + clientid + "-" + newrepositoryid)
        .setAttribute("tabindex", "0")
        .focus();
    },
    parse_repository_options: function (data, appendtolist) {
      if (appendtolist) {
        if (data.list) {
          if (!this.filelist) {
            this.filelist = [];
          }
          for (var i in data.list) {
            this.filelist[this.filelist.length] = data.list[i];
          }
        }
      } else {
        this.filelist = data.list ? data.list : null;
        this.lazyloading = {};
      }
      this.filepath = data.path ? data.path : null;
      this.objecttag = data.object ? data.object : null;
      this.active_repo = {};
      this.active_repo.issearchresult = data.issearchresult ? !0 : !1;
      this.active_repo.defaultreturntype = data.defaultreturntype
        ? data.defaultreturntype
        : null;
      this.active_repo.dynload = data.dynload ? data.dynload : !1;
      this.active_repo.pages = Number(data.pages ? data.pages : null);
      this.active_repo.page = Number(data.page ? data.page : null);
      this.active_repo.hasmorepages =
        this.active_repo.pages &&
        this.active_repo.page &&
        (this.active_repo.page < this.active_repo.pages ||
          this.active_repo.pages == -1);
      this.active_repo.id = data.repo_id ? data.repo_id : null;
      this.active_repo.nosearch = data.login || data.nosearch;
      this.active_repo.norefresh = data.login || data.norefresh;
      this.active_repo.nologin = data.login || data.nologin;
      this.active_repo.logouttext = data.logouttext ? data.logouttext : null;
      this.active_repo.logouturl = data.logouturl || "";
      this.active_repo.message = data.message || "";
      this.active_repo.help = data.help ? data.help : null;
      this.active_repo.manage = data.manage ? data.manage : null;
      this.active_repo.filereferencewarning = data.filereferencewarning
        ? data.filereferencewarning
        : null;
      this.print_header();
    },
    print_login: function (data) {
      this.parse_repository_options(data);
      var client_id = this.options.client_id;
      var repository_id = data.repo_id;
      var l = (this.logindata = data.login);
      var loginurl = "";
      var action = data.login_btn_action ? data.login_btn_action : "login";
      var form_id = "fp-form-" + client_id;
      var loginform_node = Y.Node.create(M.core_filepicker.templates.loginform);
      loginform_node.one("form").set("id", form_id);
      this.fpnode.one(".fp-content").setContent("").appendChild(loginform_node);
      var templates = {
        popup: loginform_node.one(".fp-login-popup"),
        textarea: loginform_node.one(".fp-login-textarea"),
        select: loginform_node.one(".fp-login-select"),
        text: loginform_node.one(".fp-login-text"),
        radio: loginform_node.one(".fp-login-radiogroup"),
        checkbox: loginform_node.one(".fp-login-checkbox"),
        input: loginform_node.one(".fp-login-input"),
      };
      var container;
      for (var i in templates) {
        if (templates[i]) {
          container = templates[i].get("parentNode");
          container.removeChild(templates[i]);
        }
      }
      for (var k in l) {
        if (templates[l[k].type]) {
          var node = templates[l[k].type].cloneNode(!0);
        } else {
          node = templates.input.cloneNode(!0);
        }
        if (l[k].type == "popup") {
          loginurl = l[k].url;
          var popupbutton = node.one("button");
          popupbutton.on(
            "click",
            function (e) {
              M.core_filepicker.active_filepicker = this;
              window.open(
                loginurl,
                "repo_auth",
                "location=0,status=0,width=500,height=300,scrollbars=yes"
              );
              e.preventDefault();
            },
            this
          );
          loginform_node.one("form").on(
            "keydown",
            function (e) {
              if (e.keyCode == 13) {
                popupbutton.simulate("click");
                e.preventDefault();
              }
            },
            this
          );
          loginform_node.all(".fp-login-submit").remove();
          action = "popup";
        } else if (l[k].type == "textarea") {
          if (node.one("label")) {
            node.one("label").set("for", l[k].id).setContent(l[k].label);
          }
          node.one("textarea").setAttrs({ id: l[k].id, name: l[k].name });
        } else if (l[k].type == "select") {
          if (node.one("label")) {
            node.one("label").set("for", l[k].id).setContent(l[k].label);
          }
          node
            .one("select")
            .setAttrs({ id: l[k].id, name: l[k].name })
            .setContent("");
          for (i in l[k].options) {
            node
              .one("select")
              .appendChild(
                Y.Node.create("<option/>")
                  .set("value", l[k].options[i].value)
                  .setContent(l[k].options[i].label)
              );
          }
        } else if (l[k].type == "radio") {
          node.all("label").setContent(l[k].label);
          var list = l[k].value.split("|");
          var labels = l[k].value_label.split("|");
          var radionode = null;
          for (var item in list) {
            if (radionode == null) {
              radionode = node.one(".fp-login-radio");
              radionode.one("input").set("checked", "checked");
            } else {
              var x = radionode.cloneNode(!0);
              radionode.insert(x, "after");
              radionode = x;
              radionode.one("input").set("checked", "");
            }
            radionode
              .one("input")
              .setAttrs({
                id: "" + l[k].id + item,
                name: l[k].name,
                type: l[k].type,
                value: list[item],
              });
            radionode
              .all("label")
              .setContent(labels[item])
              .set("for", "" + l[k].id + item);
          }
          if (radionode == null) {
            node.one(".fp-login-radio").remove();
          }
        } else {
          if (node.one("label")) {
            node.one("label").set("for", l[k].id).setContent(l[k].label);
          }
          node
            .one("input")
            .set("type", l[k].type)
            .set("id", l[k].id)
            .set("name", l[k].name)
            .set("value", l[k].value ? l[k].value : "");
        }
        container.appendChild(node);
      }
      if (data.login_btn_label) {
        loginform_node.all(".fp-login-submit").setContent(data.login_btn_label);
      }
      if (action == "login" || action == "search") {
        loginform_node.one(".fp-login-submit").on(
          "click",
          function (e) {
            e.preventDefault();
            this.hide_header();
            this.request(
              {
                scope: this,
                action: action == "search" ? "search" : "signin",
                path: "",
                client_id: client_id,
                repository_id: repository_id,
                form: { id: form_id, upload: !1, useDisabled: !0 },
                callback: this.display_response,
              },
              !0
            );
          },
          this
        );
      }
      if (loginform_node.one(".fp-login-submit")) {
        loginform_node.one("form").on(
          "keydown",
          function (e) {
            if (e.keyCode == 13) {
              loginform_node.one(".fp-login-submit").simulate("click");
              e.preventDefault();
            }
          },
          this
        );
      }
    },
    display_response: function (id, obj, args) {
      var scope = args.scope;
      scope.fpnode
        .all(".fp-repo.active")
        .removeClass("active")
        .setAttribute("aria-selected", "false")
        .setAttribute("tabindex", "-1");
      scope.fpnode
        .all(".nav-link")
        .removeClass("active")
        .setAttribute("aria-selected", "false")
        .setAttribute("tabindex", "-1");
      var activenode = scope.fpnode.one(
        "#fp-repo-" + scope.options.client_id + "-" + obj.repo_id
      );
      activenode
        .addClass("active")
        .setAttribute("aria-selected", "true")
        .setAttribute("tabindex", "0");
      activenode.all(".nav-link").addClass("active");
      for (var i in scope.options.repositories) {
        scope.fpnode.removeClass(
          "repository_" + scope.options.repositories[i].type
        );
      }
      if (obj.repo_id && scope.options.repositories[obj.repo_id]) {
        scope.fpnode.addClass(
          "repository_" + scope.options.repositories[obj.repo_id].type
        );
      }
      Y.one(".file-picker .fp-repo-items").focus();
      if (obj.login) {
        scope.viewbar_set_enabled(!1);
        scope.print_login(obj);
      } else if (obj.upload) {
        scope.viewbar_set_enabled(!1);
        scope.parse_repository_options(obj);
        scope.create_upload_form(obj);
      } else if (obj.object) {
        M.core_filepicker.active_filepicker = scope;
        scope.viewbar_set_enabled(!1);
        scope.parse_repository_options(obj);
        scope.create_object_container(obj.object);
      } else if (obj.list) {
        scope.viewbar_set_enabled(!0);
        scope.parse_repository_options(obj);
        scope.view_files();
      }
    },
    list: function (args) {
      if (!args) {
        args = {};
      }
      if (!args.repo_id) {
        args.repo_id = this.active_repo.id;
      }
      if (!args.path) {
        args.path = "";
      }
      this.currentpath = args.path;
      this.request(
        {
          action: "list",
          client_id: this.options.client_id,
          repository_id: args.repo_id,
          path: args.path,
          page: args.page,
          scope: this,
          callback: this.display_response,
        },
        !0
      );
    },
    populateLicensesSelect: function (licensenode, filenode) {
      if (!licensenode) {
        return;
      }
      licensenode.setContent("");
      var selectedlicense = this.options.defaultlicense;
      if (filenode) {
        selectedlicense = filenode.license;
      } else if (
        this.options.rememberuserlicensepref &&
        this.get_preference("recentlicense")
      ) {
        selectedlicense = this.get_preference("recentlicense");
      }
      var licenses = this.options.licenses;
      for (var i in licenses) {
        if (
          licenses[i].enabled == !0 ||
          (filenode !== undefined && licenses[i].shortname === filenode.license)
        ) {
          var option = Y.Node.create("<option/>")
            .set("selected", licenses[i].shortname == selectedlicense)
            .set("value", licenses[i].shortname)
            .setContent(Y.Escape.html(licenses[i].fullname));
          licensenode.appendChild(option);
        }
      }
    },
    create_object_container: function (data) {
      var content = this.fpnode.one(".fp-content");
      content.setContent("");
      var container = Y.Node.create("<object/>")
        .setAttrs({ data: data.src, type: data.type, id: "container_object" })
        .addClass("fp-object-container");
      content.setContent("").appendChild(container);
    },
    create_upload_form: function (data) {
        console.log(data)
      var client_id = this.options.client_id;
      var id = data.upload.id + "_" + client_id;
      var content = this.fpnode.one(".fp-content");
      var template_name =
        "uploadform_" + this.options.repositories[data.repo_id].type;
      var template =
        M.core_filepicker.templates[template_name] ||
        M.core_filepicker.templates.uploadform;
      content.setContent(template);
      content
        .all(".fp-file,.fp-saveas,.fp-setauthor,.fp-setlicense")
        .each(function (node) {
          node.all("label").set("for", node.one("input,select").generateID());
        });
      content.one("form").set("id", id);
      content.one(".fp-file input").set("name", "repo_upload_file");
      if (data.upload.label && content.one(".fp-file label")) {
        content.one(".fp-file label").setContent(data.upload.label);
      }
      content.one(".fp-saveas input").set("name", "title");
      content
        .one(".fp-setauthor input")
        .setAttrs({ name: "author", value: this.options.author });
      content.one(".fp-setlicense select").set("name", "license");
      this.populateLicensesSelect(content.one(".fp-setlicense select"));
      content
        .one("form")
        .appendChild(
          Y.Node.create("<input/>").setAttrs({
            type: "hidden",
            name: "itemid",
            value: this.options.itemid,
          })
        );
      var types = this.options.accepted_types;
      for (var i in types) {
        content
          .one("form")
          .appendChild(
            Y.Node.create("<input/>").setAttrs({
              type: "hidden",
              name: "accepted_types[]",
              value: types[i],
            })
          );
      }
      var scope = this;
      content.one(".fp-upload-btn").on(
        "click",
        function (e) {
          e.preventDefault();
          var license = content.one(".fp-setlicense select");
          if (this.options.rememberuserlicensepref) {
            this.set_preference("recentlicense", license.get("value"));
          }
          if (!content.one(".fp-file input").get("value")) {
            scope.print_msg(
              M.util.get_string("nofilesattached", "repository"),
              "error"
            );
            return !1;
          }
          this.hide_header();
          p_mega = [scope, client_id, scope.options.savepath, id];
          scope.request(
            {
              scope: scope,
              action: "upload",
              client_id: client_id,
              params: { savepath: scope.options.savepath },
              repository_id: scope.active_repo.id,
              form: { id: id, upload: !0 },
              onerror: function (id, o, args) {
                scope.create_upload_form(data);
              },
              callback: function (id, o, args) {
                if (o.event == "fileexists") {
                  scope.create_upload_form(data);
                  scope.process_existing_file(o);
                  return;
                }
                if (
                  scope.options.editor_target &&
                  scope.options.env == "editor"
                ) {
                  scope.options.editor_target.value = o.url;
                  scope.options.editor_target.dispatchEvent(
                    new Event("change"),
                    { bubbles: !0 }
                  );
                }
                scope.hide();
                o.client_id = client_id;
                var formcallback_scope = args.scope.options.magicscope
                  ? args.scope.options.magicscope
                  : args.scope;
                scope.options.formcallback.apply(formcallback_scope, [o]);
              },
            },
            !0
          );
        },
        this
      );
    },
    setup_toolbar: function () {
      var client_id = this.options.client_id;
      var toolbar = this.fpnode.one(".fp-toolbar");
      toolbar
        .one(".fp-tb-logout")
        .one("a,button")
        .on(
          "click",
          function (e) {
            e.preventDefault();
            if (!this.active_repo.nologin) {
              this.hide_header();
              this.request(
                {
                  action: "logout",
                  client_id: this.options.client_id,
                  repository_id: this.active_repo.id,
                  path: "",
                  callback: this.display_response,
                },
                !0
              );
            }
            if (this.active_repo.logouturl) {
              window.open(
                this.active_repo.logouturl,
                "repo_auth",
                "location=0,status=0,width=500,height=300,scrollbars=yes"
              );
            }
          },
          this
        );
      toolbar
        .one(".fp-tb-refresh")
        .one("a,button")
        .on(
          "click",
          function (e) {
            e.preventDefault();
            if (!this.active_repo.norefresh) {
              this.list({ path: this.currentpath });
            }
          },
          this
        );
      toolbar
        .one(".fp-tb-search form")
        .set("method", "POST")
        .set("id", "fp-tb-search-" + client_id)
        .on(
          "submit",
          function (e) {
            e.preventDefault();
            if (!this.active_repo.nosearch) {
              this.request(
                {
                  scope: this,
                  action: "search",
                  client_id: this.options.client_id,
                  repository_id: this.active_repo.id,
                  form: {
                    id: "fp-tb-search-" + client_id,
                    upload: !1,
                    useDisabled: !0,
                  },
                  callback: this.display_response,
                },
                !0
              );
            }
          },
          this
        );
      var managelnk = Y.Node.create("<a/>")
        .setAttrs({
          id: "fp-tb-manage-" + client_id + "-link",
          target: "_blank",
        })
        .setStyle("display", "none");
      toolbar.append(managelnk);
      toolbar
        .one(".fp-tb-manage")
        .one("a,button")
        .on("click", function (e) {
          e.preventDefault();
          managelnk.simulate("click");
        });
      var helplnk = Y.Node.create("<a/>")
        .setAttrs({ id: "fp-tb-help-" + client_id + "-link", target: "_blank" })
        .setStyle("display", "none");
      toolbar.append(helplnk);
      toolbar
        .one(".fp-tb-help")
        .one("a,button")
        .on("click", function (e) {
          e.preventDefault();
          helplnk.simulate("click");
        });
    },
    hide_header: function () {
      if (this.fpnode.one(".fp-toolbar")) {
        this.fpnode.one(".fp-toolbar").addClass("empty");
      }
      if (this.pathbar) {
        this.pathbar.setContent("").addClass("empty");
      }
    },
    print_header: function () {
      var r = this.active_repo;
      var scope = this;
      var client_id = this.options.client_id;
      this.hide_header();
      this.print_path();
      var toolbar = this.fpnode.one(".fp-toolbar");
      if (!toolbar) {
        return;
      }
      var enable_tb_control = function (node, enabled) {
        if (!node) {
          return;
        }
        node.addClassIf("disabled", !enabled).addClassIf("enabled", enabled);
        if (enabled) {
          toolbar.removeClass("empty");
        }
      };
      enable_tb_control(toolbar.one(".fp-tb-back"), !1);
      enable_tb_control(toolbar.one(".fp-tb-search"), !r.nosearch);
      if (!r.nosearch) {
        var searchform = toolbar.one(".fp-tb-search form");
        searchform.setContent("");
        this.request(
          {
            scope: this,
            action: "searchform",
            repository_id: this.active_repo.id,
            callback: function (id, obj, args) {
              if (obj.repo_id == scope.active_repo.id && obj.form) {
                searchform.setContent(obj.form);
                var searchnode = searchform.one('input[name="s"]');
                if (searchnode) {
                  searchnode.once("click", function (e) {
                    e.preventDefault();
                    this.select();
                  });
                }
              }
            },
          },
          !1
        );
      }
      enable_tb_control(toolbar.one(".fp-tb-refresh"), !r.norefresh);
      enable_tb_control(toolbar.one(".fp-tb-logout"), !r.nologin);
      enable_tb_control(toolbar.one(".fp-tb-manage"), r.manage);
      Y.one("#fp-tb-manage-" + client_id + "-link").set("href", r.manage);
      enable_tb_control(toolbar.one(".fp-tb-help"), r.help);
      Y.one("#fp-tb-help-" + client_id + "-link").set("href", r.help);
      enable_tb_control(toolbar.one(".fp-tb-message"), r.message);
      toolbar.one(".fp-tb-message").setContent(r.message);
    },
    print_path: function () {
      if (!this.pathbar) {
        return;
      }
      this.pathbar.setContent("").addClass("empty");
      var p = this.filepath;
      if (p && p.length != 0 && this.viewmode != 2) {
        for (var i = 0; i < p.length; i++) {
          var el = this.pathnode.cloneNode(!0);
          this.pathbar.appendChild(el);
          if (i == 0) {
            el.addClass("first");
          }
          if (i == p.length - 1) {
            el.addClass("last");
          }
          if (i % 2) {
            el.addClass("even");
          } else {
            el.addClass("odd");
          }
          el.all(".fp-path-folder-name").setContent(Y.Escape.html(p[i].name));
          el.on(
            "click",
            function (e, path) {
              e.preventDefault();
              this.list({ path: path });
            },
            this,
            p[i].path
          );
        }
        this.pathbar.removeClass("empty");
      }
    },
    hide: function () {
      this.selectui.hide();
      if (this.process_dlg) {
        this.process_dlg.hide();
      }
      if (this.msg_dlg) {
        this.msg_dlg.hide();
      }
      this.mainui.hide();
    },
    show: function () {
      if (this.fpnode) {
        this.hide();
        this.mainui.show();
        this.show_recent_repository();
      } else {
        this.launch();
      }
    },
    launch: function () {
      this.render();
    },
    show_recent_repository: function () {
      this.hide_header();
      this.viewbar_set_enabled(!1);
      var repository_id = this.get_preference("recentrepository");
      this.viewmode = this.get_preference("recentviewmode");
      if (this.viewmode != 2 && this.viewmode != 3) {
        this.viewmode = 1;
      }
      if (this.options.repositories[repository_id]) {
        this.list({ repo_id: repository_id });
      }
    },
    get_preference: function (name) {
      if (this.options.userprefs[name]) {
        return this.options.userprefs[name];
      } else {
        return !1;
      }
    },
    set_preference: function (name, value) {
      if (this.options.userprefs[name] != value) {
        M.util.set_user_preference("filepicker_" + name, value);
        this.options.userprefs[name] = value;
      }
    },
    in_iframe: function () {
      return window.self !== window.top;
    },
  });
  var loading = Y.one("#filepicker-loading-" + options.client_id);
  if (loading) {
    loading.setStyle("display", "none");
  }
  M.core_filepicker.instances[options.client_id] = new FilePickerHelper(
    options
  );
};
