function TagListItemViewModel(data) {
    var self = this;
    self.tagId = data['id'];
    self.tagUrl = data['url'];
    self.tag = data['tag'];
    self.isTrending = data['is_trending'];
    self.occurrences = data['occurrences'];

    return self;
};

function TagListViewModel(params) {
    var self = this;
    self.page = params.page;
    self.tags = ko.observableArray([]);

    init();

    //--------

    function init() {
        $.ajax({
            url: RESTAPI_URLS.TAGS + self.page,
            type: METHODS.GET
        }).done(function(data) {
            data.forEach(function(tag) {
                self.tags.push(new TagListItemViewModel(tag));
            });
        });

    }

};

ko.components.register('tags-list-component', {
    template: { element: 'tags-list-template' },
    viewModel: TagListViewModel
});
