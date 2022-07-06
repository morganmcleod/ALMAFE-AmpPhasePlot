'''
Interface classes for set/get/update/delete tags refering to another table via foreign key
'''
from abc import ABC, abstractmethod

class TagsInterface(ABC):
    '''
    Defines the interface for set/get/update/delete tags
    '''

    @abstractmethod
    def setTags(self, plotResultId, tagDictionary):
        '''
        Set, update, or delete tags on the specified PlotResult:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param plotResultId: int of the PlotResult to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        pass
        
    @abstractmethod
    def getTags(self, plotResultId, tagNames):       
        '''
        Retrieve tags on the specified PlotResult:
        :param plotResultId: int of the PlotResult to query
        :param tagNames: list of strings
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        pass

