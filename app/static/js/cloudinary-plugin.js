CloudinaryPlugin = {
  install : function (Vue, options) {
    // 4. add an instance method

    if(options.cloud_name &&
        options.api_key &&
        options.api_secret){

      options.secure = true
      Vue.prototype.$cloudinary = new cloudinary.Cloudinary(options);
    } else {
      console.log('Cloudinary options not valid must have cloud_name api_key and api_secret', options)
    }
  }
}