var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        heading: 'Branch',
        landed: false,

        branchId: branchid,
        branch: {},
        
        categories: [],
        subjects: [],
        exams: [],



        newExam: {
            name:'',
            tests: [],
        },

        loading: 'Loading...',
        subjectLoading: '',
        branchLoading: '',
        categoryLoading: '',
        examLoading: '',

        updateAction: false,

        error: '',
        message: '',
        initBasicForm: {
            fields:{
                name: 'empty',
            }
        },
        initBasicModal: {
            onShow: function(){
                var form = $(this).find('.form')
                form.form(app.initBasicForm)
                form.find('.ui.error.message').empty()
                form.find('.ui.checkbox').checkbox()
            },
            onApprove: function(){
                var form = $(this).find('.form')
                $(form).find('.ui.error.message').empty()
                if(!form.form('is valid')){
                    form.form('validate form')
                    return false
                }
                var data = form.form('get values')
                console.log('form data', data)
                if(!data)
                    return false
                if(data.what === 'category'){
                    if(app.updateAction){
                        app.updateCategory(data)
                    }else{
                        app.createCategory(data)
                    }
                }
                else if (data.what === 'branch'){
                    app.updateBranch(data)
                }
                else if (data.what === 'subject'){
                    if(app.updateAction){
                        app.updateSubject(data)
                    }else{
                        app.createSubject(data)
                    }
                }
                else if (data.what === 'exam'){
                    if(app.updateAction){
                        app.updateExam(data)
                    }else{
                        app.createExam(data)
                    }
                }
                else{
                    // to stop dialog closing
                    return false
                }
                return true
            }
        },
    },
    created: function(){
        this.loadv2([
        {
            name:'Categories',
            url:'/api/category/'+this.branchId+'/list',
            variableName: 'categories',
            dataInReponse: 'categories',
            default: []
        },
        {
            name:'Exams',
            url:'/api/exam/'+this.branchId+'/list',
            variableName: 'exams',
            dataInReponse: 'exams',
            default: []
        },
        {
            name:'Subjects',
            url:'/api/subject/'+this.branchId+'/list',
            variableName: 'subjects',
            dataInReponse: 'subjects',
            default: []
        },
        {
            name:'Branch',
            url:'/api/branch/' + this.branchId,
            variableName: 'branch',
            dataInReponse: 'branch',
            default: {}
        }
        ], this.afterLoading)
    },
    updated: function(){
        // initializing dropdowns and calendar here because when user
        // clicks on 'Add test' button the data changes which leads Vue to call updated
        $('.ui.dropdown').dropdown()
        $('.ui.calendar').calendar({type: 'date'})
    },
    methods: {
        afterInit: function(){
            this.loadBranch(this.branchid)
        },
        afterLoading: function(){

            var dom = $(this.$el)
            dom.find('#afterLanding').show()
            
            dom.find('#branchModal').modal(this.initBasicModal)
            dom.find('#subjectModal').modal(this.initBasicModal)
            dom.find('#catModal').modal(this.initBasicModal)
            dom.find('#examModal').modal(this.initBasicModal)
            
            dom.find('.ui.form').form(this.bothForms)

            this.landed = true
        },
        createCategory: function(catData){
            var vm = this
            this.categoryLoading = true
            var subjects = []
            if (catData.subjects){
                catData.subjects.filter((sub)=>{
                    return sub && sub !== ""
                })
            }
            var name = catData.name
            var postData = {name:name, subjects:subjects, branch_id:this.branchId}
            var url = '/api/admin/category/add'
            this.$http.post(url, postData).
            then(response => {
                if(response.body.status === 'success'){
                    vm.categories.push(response.body.category)
                    vm.showToast('Successfully added category', 'success', 'check')
                } else {
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                app.categoryLoading = false
            },
            error => {
                console.log(error)
                app.categoryLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        updateCategory: function(category){
            console.log('update', category)
            var vm = this
            this.categoryLoading = true
            var postData = {name:category.name, id:category.id}
            var url = '/api/admin/category/update/' + category.id

            this.$http.post(url, postData).
            then(response => {
                if(response.body.status === 'success'){    
                    var index = -1
                    var updatedCat = response.body.category
                    if(!updatedCat) 
                        return
                    vm.categories.forEach((cat, i) => {
                        if(cat.id === updatedCat.id){
                            index = i
                        }
                    })
                    if(index !== -1){
                        vm.$set(vm.categories, index, updatedCat)
                    }
                    var msg = "Successfully updated " + updatedCat.name
                    vm.showToast(msg, 'success', 'check')
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.categoryLoading = false
            },
            error => {
                console.log(error)
                vm.categoryLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        createBranch: function(branch){
            var vm = this
            this.branchLoading = true
            var postData = {name:branch.name, branch_id:this.branchId}
            this.$http.post('/api/admin/branch/add', postData).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    vm.showToast('Branch added', 'success', 'check')
                    vm.branches.push(response.body.branch)
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.branchLoading = false
            },
            error => {
                console.log(error)
                vm.branchLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        updateBranch(branch){
            console.log(branch)
            branch.id = parseInt(branch.id)
            var vm = this
            this.branchLoading = true
            var postData = {name:branch.name}
            this.$http.post('/api/admin/branch/update/'+branch.id, postData).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    var updatedBranch = response.body.branch
                    var index = -1
                    vm.branches.forEach((branch, i) => {
                        if(branch.id === updatedBranch.id){
                            index = i
                        }
                    })
                    if(index != -1){
                        vm.$set(vm.branches, index, updatedBranch)
                    }
                    vm.showToast('Successfully updated '+updatedBranch.name, 'success', 'check')
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.branchLoading = false
            },
            error => {
                console.log(error)
                vm.branchLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        createSubject: function(subject){
            var vm = this
            vm.subjectLoading = true
            var postData = {name:subject.name, branch_id:this.branchId}
            this.$http.post('/api/admin/subject/add', postData)
            .then(response => {
                if(response.body.status === 'success'){
                    vm.showToast('Subject added', 'success', 'check')
                    vm.subjects.push(response.body.subject)
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.subjectLoading = false
            },
            error => {
                vm.subjectLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        updateSubject: function(subject){
            console.log(subject)
            subject.id = parseInt(subject.id)
            var vm = this
            vm.subjectLoading = true
            var postData = {name:subject.name}
            this.$http.post('/api/admin/subject/update/'+subject.id, postData)
            .then(response => {
                if(response.body.status === 'success'){
                    var updatedSubject = response.body.subject
                    var index = -1
                    vm.subjects.forEach((subject, i) => {
                        if(subject.id === updatedSubject.id){
                            index = i
                        }
                    })
                    if(index != -1){
                        vm.$set(vm.subjects, index, updatedSubject)
                    }
                    vm.showToast('Successfully updated '+updatedSubject.name, 'success', 'check')
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.subjectLoading = false
            },
            error => {
                vm.subjectLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        createExam: function(exam){
            var vm = this
            vm.examLoading = true
            var postData = {name:exam.name, branch_id:this.branchId}
            this.$http.post('/api/admin/exam/add', postData)
            .then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    vm.showToast('Exam added', 'success', 'check')
                    vm.exams.push(response.body.exam)
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.examLoading = false
            },
            error => {
                vm.examLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })  
        },
        showCreateCategory: function(){
            this.updateAction = false
            var form = $('#catModal .form')
            var formData = {name:'',
            subjects:[],
            id:undefined,
            what:'category'}
            form.form("set values", formData)
            form.find('.checkbox').checkbox('enable')
            this.showModal('catModal')
        },
        showUpdateCategory: function(category){
            this.updateAction = true
            if(category){
                var form = $('#catModal')
                var formData = Object.assign({}, category)
                formData.what = 'category'
                form.form('set values', formData)
                form.find('.checkbox').checkbox('disable')
                this.showModal('catModal')
            }else{
                vm.showToast('Click on invalid category', 'warn', 'info')
            }
        },
        showCreateBranch: function(){
            this.updateAction = false
            var form = $('#branchModal').find('.form')
            var formData = {what:'branch'}
            form.form('set values', formData)
            this.showModal('branchModal')
        },
        showUpdateBranch: function(branch){
            this.updateAction = true
            var form = $('#branchModal').find('.form')
            var formData = Object.assign({}, branch)
            formData.what = 'branch'
            form.form('set values', formData)
            this.showModal('branchModal')
        },
        showCreateSubject: function(){
            this.updateAction = false
            var form = $('#subjectModal').find('.form')
            var formData = {what:'subject'}
            form.form('set values', formData)
            this.showModal('subjectModal')
        },
        showUpdateSubject: function(subject){
            this.updateAction = true
            var form = $('#subjectModal').find('.form')
            var formData = Object.assign({}, subject)
            formData.what = 'subject'
            form.form('set values', formData)
            this.showModal('subjectModal')
        },
        showCreateExam: function(){
            this.updateAction = false
            this.showModal('examModal')
        },
        getSubjectNames: function(ids){
            var vm = this
            var names = ''
            if(!ids)
                return names
            ids.forEach((id, index)=>{
                var tmpName = vm.getSubjectName(id)
                if(tmpName){
                    names += tmpName + ', '
                }
            })
            if(names)
                return names.substring(0, names.length-2)
            return names
        },
    },
});