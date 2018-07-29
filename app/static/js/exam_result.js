var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        landed: false,
        loading: '',
        error: '',
        message: '',

        me: undefined,
        branches: [],
        exams: [],
        marks: {},
        subjects: [],
        students: [],
        categories: [],
        gradeRules: [],
        faculties: [],

        selectedBranch: undefined,
        selectedExam: undefined,
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
        ], this.init)
    },
    updated: function(){
        $(this.$el).find('table.sortable').tablesort()
    },
    watch: {
        selectedBranch: function(){
            this.loadv2([{
                name:'Exams',
                url:'/api/exam/'+this.selectedBranch.id+'/list',
                variableName: 'exams',
                dataInReponse: 'exams'
            },
            {
                name:'Categories',
                url:'/api/category/'+this.selectedBranch.id+'/list',
                variableName: 'categories',
                dataInReponse: 'categories'
            },
            {
                name:'Grades',
                url:'/api/grade/'+this.selectedBranch.id+'/list',
                variableName: 'gradeRules',
                dataInReponse: 'grades'
            },
            {
                name:'Faculty',
                url:'/api/admin/faculty/'+this.selectedBranch.id+'/list',
                variableName: 'faculties',
                dataInReponse: 'faculties'
            }
            ])
        },
        selectedExam: function(){
            this.loadv2([
            {
                name:'Students',
                url:'/api/student?ids=' + this.selectedExam.students,
                variableName: 'students',
                dataInReponse: 'students'
            },
            {
                name:'Subjects',
                url:'/api/subject/'+this.selectedBranch.id+'/list',
                variableName: 'subjects',
                dataInReponse: 'subjects'
            },
            {
                name:'Marks',
                url:'/api/admin/marks/exam/'+this.selectedExam.id,
                variableName: 'marks',
                dataInReponse: 'marks'
            }
            ], this.fixStudentCategory)
        }
    },
    computed: {
    },
    methods: {
        init: function(){
            this.branches.forEach(branch => {
                if(branch.id === this.branchId)
                    this.branch = branch
            })
            var dom = $(this.$el)
            dom.find('#afterLanding').show()
            dom.find('.ui.dropdown').dropdown()
            this.landed = true
        },
        onBranchChange: function(){
            var branchId = $('#branchDropDown').dropdown('get value')
            var branchId = parseInt(branchId)
            var index = -1
            this.branches.forEach((branch, i) => {
                if(branch.id === branchId){
                    index = i
                }
            })
            if(index != -1){
                this.selectedBranch = this.branches[index]
            }
        },
        onExamChange: function(){
            var examId = $('#examDropDown').dropdown('get value')
            var examId = parseInt(examId)
            var index = -1
            this.exams.forEach((exam, i) => {
                if(exam.id === examId){
                    index = i
                }
            })
            if(index != -1){
                this.selectedExam = this.exams[index]
            }
        },
        getMarks: function(std, testId){
            testId = parseInt(testId)
            var marks = this.marks[testId]
            if(!marks){
                return
            }
            var mark_value = undefined
            marks.forEach(mark=>{
                if(mark.student_id===std.id){
                    mark_value = mark.marks
                }
            })
            return mark_value
        },
        fixStudentCategory: function(){
            console.log('called me', this.students)
            this.students.forEach((std, stdidx) => {
                this.selectedExam.tests.forEach(test => {
                    if (test.students.indexOf(std.id) != -1){
                        std.category = test.category
                        this.$set(std, this.students, stdidx)
                    }
                })
            })
        },
        getStudentByIds: function(ids){
            return this.students.filter(std => {
                return ids.indexOf(std.id) != -1
            })
        },
        getPercent: function(std, test){
            if(!std || !test)
                return
            var mo = this.getMarks(std, test.id)
            var mm = test.max_marks
            if (!mo || !mm)
                return
            mm = parseInt(mm) || 0
            var percentage = 0
            if (mm > 0)
                percentage = (mo / mm * 100).toFixed(2)
            return percentage
        },
        _getGrade: function(std, test){
            var percent = this.getPercent(std, test)
            if(!percent)
                return
            percent = Math.round(percent)
            var grade = {}
            this.gradeRules.forEach(gRule=>{
                if(gRule.min <= percent && gRule.max >= percent)
                    grade = gRule
            })
            return grade
        },
        getGrade: function(std, test){
            var grade = this._getGrade(std, test)
            if(grade)
                return grade.grade
        },
        getGradeDescription: function(std, test){
            var grade = this._getGrade(std, test)
            if(grade)
                return grade.comment
        },
    }
})