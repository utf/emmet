from maggma.builder import Builder

__author__ = "Shyam Dwaraknath"
__email__ = "shyamd@lbl.gov"

class TaskTagger(Builder):
    def __init__(self, tasks, tag_defs, tags, **kwargs):
        """
        Creates task_types from tasks and type definitions

        Args:
            tasks (Store): Store of task documents
            tag_defs (Store): Store of tag_definitions
            tags (Store): Store of tags for tasks
        """
        self.tasks = tasks
        self.tags = tags
        self.tag_defs = tag_defs

        super().__init__(sources=[tasks, tag_defs],
                         targets=[tags],
                         **kwargs)

    def get_items(self):
        """
        Returns all task docs and tag definitions to process

        Returns:
            generator or list of task docs and tag definitions
        """

        all_task_ids = self.tasks.collection.distinct("task_id", {"state": "successful"})

        # If there is a new task type definition, re-process the whole collection
        if self.tag_defs.last_updated() > self.tags.last_updated():
            to_process = set(all_task_ids)
        else:
            previous_task_ids = self.tags.collection.distinct("task_id", {"task_type": {"$exists": 0}})
            to_process = set(all_task_ids) - set(previous_task_ids)

        tag_defs = list(self.tag_defs.collection.find())

        for t_id in to_process:
            print("Processing task_id: {}".format(t_id))
            try:
                yield {"task_doc": self.tasks.collection.find_one({"task_id": t_id}),
                       "tag_defs": tag_defs}
            except:
                import traceback
                print("Problem processing task_id: {}".format(t_id))

    def process_item(self, item):
        """
        Find the task_type for the item 
        
        Args:
            item ((dict,[dict])): a task doc and a list of possible tag definitions
        """
        task_doc = item["task_doc"]
        tag_defs = item["tag_defs"]

        scores = [self.task_matches_def(task_doc,tag_def)
                  for tag_def in tag_defs]

        if max(scores) > 0:
            tag_def = tag_defs[scores.index(max(scores))]
            return {"task_id": task_doc["task_id"],
                        "task_type": tag_def["task_type"]}
        pass

    def update_targets(self, items):
        """
        Inserts the new task_types into the tags collection
        
        Args:
            items ([dict]): task_type dicts to insert into tags collection
        """
        for doc in items:
            self.tags.collection.update({'task_id': doc['task_id']}, doc, upsert=True)

    def finalize(self):
        pass

    # TODO: Add in more sophisticated and generic matching criteria for any calculation code
    def task_matches_def(self, task_doc, tag_def):
        """
        Determines a match score to a tag type definition
        
        Args:
            task_doc (dict): task_document with original input
            tag_def (dict): dictionary with EXACT, GREATER THAN and LESS THAN criteria for matching a task_type
            
        """
        total_score = 0
        for k, v in tag_def.get("EXACT",{}).items():
            if task_doc['input_orig']['INCAR'].get(k) is not v[0]:
                pass
            else:
                total_score += v[1]

        for k, v in tag_def.get("GREATER",{}).items():
            if task_doc['input_orig']['INCAR'].get(k, 1E10) < v[0]:
                pass
            else:
                total_score += v[1]

        for k, v in tag_def.get("LESS",{}).items():
            if task_doc['input_orig']['INCAR'].get(k, 0) > v[0]:
                pass
            else:
                total_score += v[1]

        return total_score