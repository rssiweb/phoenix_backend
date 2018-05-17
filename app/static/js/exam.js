Vue.use(Toasted, {
    iconPack : 'fontawesome'
})

var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Exam Center',
        landed: true,
        
        error: '',
        message: '',
        loading: 'Loading ...',
    },
    created: function(){
  
    },
    updated: function(){
        
    },
    methods: {
    }
})