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
        grades: [],
        distributionTypes: [],
        distributionItemTypes: [],
        distributionItems: [],

        newExam: {
            name:'',
            tests: [],
        },

        loading: 'Loading...',
        subjectLoading: '',
        branchLoading: '',
        categoryLoading: '',
        examLoading: '',
        gradeLoading: '',
        distributionTypeLoading: '',
        distributionItemTypeLoading: '',
        distributionItemLoading: '',

        updateAction: false,

        error: '',
        message: '',
        showModalSettings: {
            'gradeModal':{
                modal_sel: '#gradeModal',
                form_sel: '.form',
                defaults: {what:'grade'},
            },

            'distribution-type-modal': {
                modal_sel: '#distribution-type-modal',
                form_sel: '.form',
                defaults: {what:'dist_type'},
            },
            'distribution-item-type-modal': {
                modal_sel: 'distribution-item-type-modal',
                form_sel: '.form',
                defaults: {what:'dist_item_type'},
            },
            'distribution-item-modal': {
                modal_sel: 'distribution-item-modal',
                form_sel: '.form',
                defaults: {what:'dist_item'},
            },
        },
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
                else if (data.what === 'grade'){
                    if(app.updateAction || app.is_update_action){
                        app.updateGrade(data)
                    }else{
                        app.createGrade(data)
                    }
                }
                else if (data.what === 'dist_type'){
                    if(app.updateAction){
                        app.updateDistType(data)
                    }else{
                        app.createDistType(data)
                    }
                }
                else if (data.what === 'dist_item_type'){
                    if(app.updateAction){
                        app.updateDistItemType(data)
                    }else{
                        app.createDistItemType(data)
                    }
                }
                else if (data.what === 'dist_item'){
                    if(app.updateAction){
                        app.updateDistItem(data)
                    }else{
                        app.createDistItem(data)
                    }
                }
                else{
                    // to stop dialog closing
                    return false
                }
                return true
            }
        },
        items: [
            {
                name:"Category",
                index: 1,
            },
            {
                name:"Subjects",
                index: 2,
            },
            {
                name:"Examinations",
                index: 3,
            },
            {
                name:"Grade",
                index: 4,
            },
            {
                name:"Distribution Types",
                index: 5,
            },
            {
                name:"Distribution Item Types",
                index: 6,
            },
            {
                name:"Distribution Items",
                index: 7,
            },
        ],
        active_item: undefined
    },
    created: function(){
        this.$data.active_item = this.$data.items[0]
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
        },
        {
            name:'Grades',
            url:'/api/grade/' + this.branchId+ '/list',
            variableName: 'grades',
            dataInReponse: 'grades',
            default: []
        },
        {
            name:'Distribution Types',
            url:'/api/admin/dist_type/list',
            variableName: 'distributionTypes',
            dataInReponse: 'distribution_types',
            default: []
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
            dom.find('#gradeModal').modal(this.initBasicModal)
            dom.find('#distribution-type-modal').modal(this.initBasicModal)
            dom.find('#distribution-item-type-modal').modal(this.initBasicModal)
            dom.find('#distribution-item-modal').modal(this.initBasicModal)

            dom.find('.ui.form').form(this.bothForms)

            this.landed = true
            this.grades.sort(function(a,b){
                return b.min - a.min
            })
            this.exams.sort(function(a,b){
                return b.start_date - a.start_date
            })
        },
        createCategory: function(category){
            var vm = this
            this.categoryLoading = true
            var subjects = []
            if (category.subjects.length > 0){
                subjects = category.subjects.filter((sub)=>{
                    return sub && sub !== ""
                })
            }
            var name = category.name
            var postData = {name:name, subjects: subjects, branch_id:this.branchId}
            var url = '/api/admin/category/add'
            vm.showToast('Adding '+category.name, 'info', 'hourglass-o', true)
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

            vm.showToast('Updating '+category.name, 'info', 'hourglass-o', true)
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
        updateBranch(branch){
            branch.id = parseInt(branch.id)
            var vm = this
            this.branchLoading = true
            var postData = {name:branch.name}
            vm.showToast('Updating '+branch.name, 'info', 'hourglass-o', true)
            this.$http.post('/api/admin/branch/update/'+branch.id, postData).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    var updatedBranch = response.body.branch
                    if(branch.id === updatedBranch.id){
                        vm.branch = updatedBranch
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
            vm.showToast('Adding '+subject.name, 'info', 'hourglass-o', true)
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
            vm.showToast('Updating '+subject.name, 'info', 'hourglass-o', true)
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
            vm.showToast('Adding '+exam.name, 'info', 'hourglass-o', true)
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
        createGrade: function(grade){
            var vm = this
            vm.gradeLoading = true
            var url =  '/api/admin/grade/add/' + this.branchId
            vm.$http.post(url, grade)
            .then(response => {
                if(response.body.status === 'success'){
                    vm.grades.push(response.body.grade)
                    var msg = 'Grade added Successfully'
                    vm.showToast(msg, 'success', 'check')
                } else {
                    var msg = response.body.statusText || 'Unexpected error occurred'
                    vm.showToast(msg, 'warn', 'close')
                }
                vm.gradeLoading = false
            },
            error => {
                var msg = response.statusText || 'Unexpected error occurred'
                vm.showToast(msg, 'warn', 'close')
                vm.gradeLoading = false
            })
        },
        updateGrade: function(grade){
            var vm = this
            vm.gradeLoading = true
            var url = '/api/admin/grade/update/' + this.branchId + '/' + grade.id
            vm.$http.post(url, grade)
            .then(response => {
                if(response.body.status === 'success'){
                    var updatedGrade = response.body.grade
                    vm.grades.forEach((grade, index) => {
                        if (updatedGrade.id === grade.id){
                            vm.$set(vm.grades, index, updatedGrade)
                        }
                    })
                    var msg = 'Grade updated Successfully'
                    vm.showToast(msg, 'success', 'check')
                } else {
                    var msg = response.body.statusText || 'Unexpected error occurred'
                    vm.showToast(msg, 'warn', 'close')
                }
                vm.gradeLoading = false
            },
            error => {
                var msg = response.statusText || 'Unexpected error occurred'
                vm.showToast(msg, 'warn', 'close')
                vm.gradeLoading = false
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
        showUpdateBranch: function(){
            this.updateAction = true
            var form = $('#branchModal').find('.form')
            var formData = Object.assign({}, this.branch)
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
        showCreateGrade: function(){
            this.updateAction = false
            var form = $('#gradeModal').find('.form')
            var formData = {what:'grade', min:undefined, max: undefined, comment:undefined, grade:undefined}
            form.form('set values', formData)
            this.showModal('gradeModal')
        },
        showUpdateGrade: function(grade){
            this.updateAction = true
            var form = $('#gradeModal').find('.form')
            var formData = Object.assign({}, grade)
            formData.what = 'grade'
            form.form('set values', formData)
            this.showModal('gradeModal')
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
        set_active_item: function(item){
            this.$data.active_item = item
        },
        createDistType: function(distType){
            var vm = this
            vm.distributionItemTypeLoading = true
            this.$http.post('/api/admin/dist_type/add', distType)
            .then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    vm.distributionTypes.push(response.body.dist_type)
                    vm.showToast(msg, 'success', 'tick')
                }
                else {
                    var msg = response.body.statusText || 'Unexpected error occurred'
                    vm.showToast(msg, 'warn', 'close')
                }
                vm.distributionItemTypeLoading = false
            },
            error=>{
                console.log(error)
                vm.distributionItemTypeLoading = false
            })
        },
        updateDistType: function(distType){

        },
        updateDistItemType: function(distItemType){

        },
        updateDistItem: function(distItem){

        },
    },
});