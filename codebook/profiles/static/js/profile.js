function ProfileViewModel(params) {
    self = this;
    self.userId = params.user_id;
    self.profileId = params.id;
    self.profileUrl = ko.observable('');
    self.firstName = ko.observable('');
    self.lastName = ko.observable('');
    self.fullName = ko.computed(function() {
        return self.firstName() + " " + self.lastName();
    }, this);
    self.following = ko.observable(false);
    self.reputation = ko.observable('');
    self.answersCount = ko.observable(0);
    self.questionsCount = ko.observable(0);
    self.followedBy = ko.observable(0);
    self.questionContainer = new QuestionContainer();
    self.answers = ko.observableArray([]);
    self.append = true;

    self.follow = follow;

    init();


    //---------

    function init() {
        $.ajax({
            url: RESTAPI_URLS.PROFILES + self.profileId + '/',
            type: METHODS.GET
        }).done(function(data) {
            self.profileUrl(data['url']);
            self.reputation(data['reputation']);
            self.firstName(data['user']['first_name']);
            self.lastName(data['user']['last_name']);
            self.answersCount(data['answers_count']);
            self.questionsCount(data['questions_count']);
            self.followedBy(data['followed_by']);
        });
        $.ajax({
            url: RESTAPI_URLS.PROFILES + self.profileId + PROFILE_PAGES.QUESTIONS,
            type: METHODS.GET
        }).done(function(data) {
            data.forEach(function(question){
                self.questionContainer.questions.push(new QuestionListItemViewModel(question));
            });
        });
        $.ajax({
            url: RESTAPI_URLS.PROFILES + self.profileId + PROFILE_PAGES.ANSWERS,
            type: METHODS.GET
        }).done(function(data) {
            data.forEach(function(answer){
                self.answers.push(new AnswerListItemViewModel(answer));
            });
        });
        $.ajax({
            url: RESTAPI_URLS.PROFILES + self.profileId + RESTAPI_URLS.FOLLOW,
            type: METHODS.GET
        }).done(function(data) {
            self.following(data['following']);
        });
    }

    function follow() {
        var url = RESTAPI_URLS.PROFILES + self.profileId;
        var update = 0;
        if (self.following()) {
            url += RESTAPI_URLS.UNFOLLOW;
            update = -1
        } else {
            url += RESTAPI_URLS.FOLLOW;
            update = 1
        }
        $.ajax({
            url: url,
            method: METHODS.POST,
        }).done(function(data) {
            self.following(data['following']);
            self.followedBy(self.followedBy() + update);
        });
    };

}

ko.components.register('profile-component', {
    template: { element: 'profile-template' },
    viewModel: ProfileViewModel
});

ko.applyBindings();
