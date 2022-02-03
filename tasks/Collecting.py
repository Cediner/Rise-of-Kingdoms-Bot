from tasks.Task import Task
import traceback

from tasks.constants import TaskName, BuildingNames


class Collecting(Task):
    def __init__(self, bot):
        super().__init__(bot)

    def do(self, next_task=TaskName.CLAIM_QUEST):
        super().set_text(title='Collecting Resource, Troops, and Help Alliance', remove=True)
        super().set_text(insert='Init view')

        try:
            super().back_to_home_gui()
            super().home_gui_full_view()

            super().menu_should_open(False)

            x_e, y_e = 105, 125

            troop_array = [BuildingNames.BARRACKS.value,
                           BuildingNames.ARCHERY_RANGE.value,
                           BuildingNames.STABLE.value,
                           BuildingNames.SIEGE_WORKSHOP.value]
            resource_array = [BuildingNames.FARM.value,
                              BuildingNames.LUMBER_MILL.value,
                              BuildingNames.QUARRY.value,
                              BuildingNames.GOLDMINE.value]
            alliance_array = [BuildingNames.ALLIANCE_CENTER.value]

            full_array = []

            if self.bot.config.enableCollectingTroops is True:
                append_array(troop_array, full_array)
            if self.bot.config.enableCollectingResource is True:
                append_array(resource_array, full_array)
            if self.bot.config.enableCollectingHelp is True:
                append_array(alliance_array, full_array)

            for name in full_array:
                x, y = self.bot.building_pos[name]
                self.set_text(insert='tap {} at position ({},{})'.format(name, x, y))
                self.tap(x, y)
                self.tap(x_e, y_e, 0.2)

        except Exception as e:
            traceback.print_exc()
            return next_task
        return next_task


def append_array(array_source, array_dest):
    for e in array_source:
        array_dest.append(e)
