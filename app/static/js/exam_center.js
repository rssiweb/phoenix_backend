var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Exam Center',
        landed: false,

        students: [],
        branches: [],
        categories: [],
        exams: [],
        subjects: [],
        marks: [],
        tests: [],
        marks: [],
        result: {},
        gradeRules: [],
        branch: {},
        me: {},

        selectedTestId: -1,
        studentCatFilter: '',

        examLoading: false,
        marksLoading: false,

        error: '',
        message: '',
        loading: 'Loading ...',
    },
    created: function(){
        this.loadv2([
        {
            name:'Branches',
            url:'/api/branch/list',
            variableName: 'branches',
            dataInReponse: 'branches'
        },
        {
            name: 'Me',
            url: '/api/myprofile',
            variableName: 'me',
            dataInReponse: 'me'
        }
        ], this.after)
    },
    updated: function(){
        console.log('updated')
        var dom = $(this.$el)
        dom.find('#afterLanding').show()
        dom.find('.ui.dropdown').dropdown()
        this.landed = true
    },
    watch: {
        branch: function(){
            if(this.branch.id){
                this.examLoading = true
                this.loadv2([
                {
                    name:'Students',
                    url:'/api/student/'+this.branch.id+'/list',
                    variableName: 'students',
                    dataInReponse: 'students'
                },
                {
                    name:'Categories',
                    url:'/api/category/'+this.branch.id+'/list',
                    variableName: 'categories',
                    dataInReponse: 'categories'
                },
                {
                    name:'Exams',
                    url:'/api/exam/'+this.branch.id+'/list',
                    variableName: 'exams',
                    dataInReponse: 'exams'
                },
                {
                    name:'Subjects',
                    url:'/api/subject/'+this.branch.id+'/list',
                    variableName: 'subjects',
                    dataInReponse: 'subjects'
                },
                {
                    name:'Grades',
                    url:'/api/grade/'+this.branch.id+'/list',
                    variableName: 'gradeRules',
                    dataInReponse: 'grades'
                }
                ],this.afterExamLoaded)
            }
        },
        selectedTestId: function(){
            if(this.branch.id && this.selectedTestId){
                this.marksLoading = true
                this.loadv2([
                {
                    name:'Marks',
                    url:'/api/marks/'+this.selectedTestId,
                    variableName: 'marks',
                    dataInReponse: 'marks',
                    default: []
                },], this.afterMarksLoad)
            }
        }
    },
    computed: {
        filteredStudents: function(){
            return this.students.filter((std) => {
                return std.category === this.studentCatFilter
            })
        },
        selectedTest: function(){
            var test = undefined
            this.tests.forEach(t => {
                if(t.id === this.selectedTestId)
                    test = t
            })
            return test
        }
    },
    methods: {
        after: function(){
            this.heading = 'Exam Center'
            this.branches.forEach(branch=>{
                if(branch.id===this.branchId)
                    this.branch = branch
            })
        },
        afterExamLoaded: function(){
            this.examLoading = false
        },
        afterMarksLoad: function(){
            this.marksLoading = false
            this.marks.forEach(mark=>{
                var data  = {marks: mark.marks, comment: mark.comments, marksSaving: false, commentSaving:false}
                this.$set(this.result, mark.student_id, data)
            })
        },
        onBranchChange: function(){
            var data = $('#branchForm').form('get values')
            var selectedBranchId = parseInt(data.branch)
            var index = -1
            this.branches.forEach((branch, i) => {
                if(branch.id === selectedBranchId){
                    index = i
                }
            })
            if(index != -1){
                this.branch = this.branches[index]
            }
        },
        onExamChange: function(){
            var data = $('#testCodeForm').form('get values')
            var selectedExamId = parseInt(data.exam)
            var index = -1
            this.exams.forEach((exam, i) => {
                if(exam.id === selectedExamId){
                    index = i
                }
            })
            if(index != -1){
                $('#testDropdown').dropdown('clear')
                this.tests = []
                this.result = {}
                this.studentCatFilter = ''
                var allTests = this.exams[index].tests
                this.tests = allTests.filter(test => {
                    return this.me.admin || test.evaluator === this.me.id
                })
            }
        },
        onTestChange: function(){
            var data = $('#testCodeForm').form('get values')
            if(!data.test) {
                return
            }
            this.selectedTestId = parseInt(data.test)
            var test = undefined
            this.tests.forEach((t, i)=>{
                if(t.id === this.selectedTestId){
                    test = t
                }
            })
            if(!test){
                return
            }
            this.studentCatFilter = test.category
            this.result = {}
        },
        setObtainedMarks: function(std_id, event){
            var vm = this
            console.log('setObtainedMarks', std_id, event.target.value)
            var setCommentAlso = false
            var data = this.result[std_id]
            if(!data){
                data = {}
                setCommentAlso = true
            }
            var marks = event.target.value
            if(marks > this.selectedTest.max_marks){
                return
            }

            data['marks'] = marks
            data['marksSaving'] = true

            if(setCommentAlso){
                var grade = this.gradeFor(this.percentOf(event.target.value))
                data['comment'] = grade.comment
                data['commentSaving'] = true
            }
            this.$set(this.result, std_id, data)
            // http call delay
            var url = '/api/marks/set/' + this.selectedTest.id + '/' + std_id
            this.$http.post(url, data)
            .then(response => {
                console.log(response)
                var data = vm.result[std_id]
                data.marksSaving = false
                data.commentSaving = false
                vm.$set(vm.result, std_id, data)
            },
            error => {
                console.log(error)
                var data = vm.result[std_id]
                data.marksSaving = false
                data.commentSaving = false
                vm.$set(vm.result, std_id, data)
            })
        },
        setComments: function(std_id, event){
            var vm = this
            console.log('setComments', std_id, event.target.value)
            var data = this.result[std_id] || {}
            data['comment'] = event.target.value
            data['commentSaving'] = true

            this.$set(this.result, std_id, data)
            var url = '/api/marks/set/' + this.selectedTest.id + '/' + std_id
            this.$http.post(url, data)
            .then(response => {
                console.log(response)
                var data = vm.result[std_id]
                data.commentSaving = false
                vm.$set(vm.result, std_id, data)
            },
            error => {
                console.log(error)
                var data = vm.result[std_id]
                data.commentSaving = false
                vm.$set(vm.result, std_id, data)
            })
        },
        gradeFor: function(percent){
            percent = Math.round(percent)
            var grade = {}
            this.gradeRules.forEach(gRule=>{
                if(gRule.min <= percent && gRule.max >= percent)
                    grade = gRule
            })
            return grade
        },
        getGrade: function(id){
            var percent = this.getPercentage(id)
            return this.gradeFor(percent)
        },
        percentOf: function(mo){
            var mo = parseInt(mo)
            var mm = this.selectedTest.max_marks
            if(mm)
                mm = parseInt(mm) || 0
            var percentage = 0
            if (mm > 0)
                percentage = (mo / mm * 100).toFixed(2)
            return percentage
        },
        getPercentage: function(id){
            var data = this.result[id]
            if(!data)
                return undefined
            var mo = data.marks
            if(!mo)
                return undefined
            return this.percentOf(mo)
        },
        getComment: function(id){
            // intentially leaving for undefined
            var data = this.result[id]
            if(data)
                return data.comment
        },
        getMarks: function(id){
          var data = this.result[id]
            if(data)
                return data.marks
        }
    }
})