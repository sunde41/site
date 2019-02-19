/**
 * @license Copyright (c) 2003-2017, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

 CKEDITOR.editorConfig = function( config ) {

     config.language = 'ko';
     config.toolbar = [
       { name: 'MAX', items:['Maximize'] },
       { name: 'insert', items:['CodeSnippet','addImage','Table','Link','Unlink','Blockquote','HorizontalRule'] },
       { name: 'basicstyles', items: ['Bold', 'Italic','Underline','Strike', 'TextColor','BGColor', '-', 'RemoveFormat' ] },
       { name: 'paragraph', items: [ 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-','JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] }
     ];

     config.removeDialogTabs = 'image:advanced;link:advanced';
     config.removeButtons = 'addFile,Anchor,Image,Subscript,Superscript,Format';
     config.extraPlugins = 'simpleuploads,confighelper';
     config.codeSnippet_theme = 'github-gist';
     config.codeSnippet_languages = {
         python: 'Python'
     };
     config.placeholder = '내용을 입력하세요...';
     config.filebrowserUploadUrl = '/upload';
     config.filebrowserImageUploadUrl = '/upload';
     config.height = 300
 };
