import traceback

from filepath.constants import MAP
from filepath.file_relative_paths import BuffsImageAndProps, ItemsImageAndProps, ImagePathAndProps
from tasks.Task import Task
from tasks.constants import TaskName, Resource


class GatherResource(Task):

    def __init__(self, bot):
        super().__init__(bot)
        self.max_query_space = 5

    def do(self, next_task=TaskName.BREAK):
        magnifier_pos = (60, 540)
        self.set_text(title='Gather Resource', remove=True)
        self.call_idle_back()

        if self.bot.config.useGatheringBoosts:
            b_buff_props = BuffsImageAndProps.ENHANCED_GATHER_BLUE.value
            p_buff_props = BuffsImageAndProps.ENHANCED_GATHER_PURPLE.value
            b_item_props = ItemsImageAndProps.ENHANCED_GATHER_BLUE.value
            p_item_props = ItemsImageAndProps.ENHANCED_GATHER_PURPLE.value
            has_blue = self.has_buff(MAP, b_buff_props)
            has_purple = self.has_buff(MAP, p_buff_props)
            if not has_blue and not has_purple:
                self.set_text(insert='use gathering boosts')
                self.use_item(MAP, [b_item_props, p_item_props])
            else:
                self.set_text(insert="gathering boosts buff is already on")

        last_resource_pos = []
        should_decreasing_lv = False
        resource_icon_pos = [
            (450, 640),
            (640, 640),
            (830, 640),
            (1030, 640)
        ]
        try:
            chose_icon_pos = resource_icon_pos[0]
            self.back_to_map_gui()
            resourse_code = self.get_min_resource()
            self.back_to_map_gui()

            if resourse_code == Resource.FOOD.value:
                chose_icon_pos = resource_icon_pos[0]
                self.set_text(insert="Search food")

            elif resourse_code == Resource.WOOD.value:
                chose_icon_pos = resource_icon_pos[1]
                self.set_text(insert="Search wood")

            elif resourse_code == Resource.STONE.value:
                chose_icon_pos = resource_icon_pos[2]
                self.set_text(insert="Search stone")

            elif resourse_code == Resource.GOLD.value:
                chose_icon_pos = resource_icon_pos[3]
                self.set_text(insert="Search gold")

            if self.bot.config.holdOneQuerySpace:
                space = self.check_query_space()
                if space <= 1:
                    self.set_text(insert="Match query space less or equal to 1, stop!")
                    return next_task

            # tap on magnifier
            x, y = magnifier_pos
            self.tap(x, y, 0.5)
            self.tap(chose_icon_pos[0], chose_icon_pos[1], 0.5)
            search_pos = self.gui.check_any(ImagePathAndProps.RESOURCE_SEARCH_BUTTON_IMAGE_PATH.value)[2]
            dec_pos = self.gui.check_any(ImagePathAndProps.DECREASING_BUTTON_IMAGE_PATH.value)[2]
            inc_pos = self.gui.check_any(ImagePathAndProps.INCREASING_BUTTON_IMAGE_PATH.value)[2]
            self.tap(inc_pos[0] - 33, inc_pos[1], 0.3)

            repeat_count = 0
            for i in range(10):

                # open search resource
                if len(last_resource_pos) > 0:
                    self.back_to_map_gui()

                    if self.bot.config.holdOneQuerySpace:
                        space = self.check_query_space()
                        if space <= 1:
                            self.set_text(insert="Match query space less or equal to 1, stop!")
                            return next_task

                    self.tap(x, y, 1)
                    self.tap(chose_icon_pos[0], chose_icon_pos[1], 0.5)

                # decreasing level
                if should_decreasing_lv:
                    self.set_text(insert="Decreasing level by 1")
                    self.tap(dec_pos[0], dec_pos[1], 0.3)

                for j in range(5):
                    self.tap(search_pos[0], search_pos[1], 1)
                    is_found, _, _ = self.gui.check_any(ImagePathAndProps.RESOURCE_SEARCH_BUTTON_IMAGE_PATH.value)
                    if not is_found:
                        break
                    self.set_text(insert="Not found, decreasing level by 1 [{}]".format(j))
                    self.tap(dec_pos[0], dec_pos[1], 0.3)

                self.set_text(insert="Resource found")
                self.tap(640, 320, 0.5)

                # check is same pos
                new_resource_pos = self.gui.resource_location_image_to_string()

                # small fix
                if new_resource_pos in last_resource_pos:
                    self.tap(x, y, 0.5)
                    self.tap(chose_icon_pos[0], chose_icon_pos[1], 0.5)
                    self.tap(search_pos[0], search_pos[1], 1)

                    self.set_text(insert="Resource found")
                    self.tap(640, 320, 0.5)
                    new_resource_pos = self.gui.resource_location_image_to_string()

                if new_resource_pos in last_resource_pos:
                    should_decreasing_lv = True
                    repeat_count = repeat_count + 1
                    self.set_text(insert="Resource point is already in match")
                    if repeat_count > 4:
                        self.set_text(insert="stuck! end task")
                        break
                    else:
                        continue
                last_resource_pos.append(new_resource_pos)
                should_decreasing_lv = False
                gather_button_pos = self.gui.check_any(ImagePathAndProps.RESOURCE_GATHER_BUTTON_IMAGE_PATH.value)[2]
                self.tap(gather_button_pos[0], gather_button_pos[1], 1)
                pos = self.gui.check_any(ImagePathAndProps.NEW_TROOPS_BUTTON_IMAGE_PATH.value)[2]
                if pos is None:
                    self.set_text(insert="Not more space for march")
                    return next_task
                new_troops_button_pos = pos
                self.tap(new_troops_button_pos[0], new_troops_button_pos[1], 1)
                if self.bot.config.gatherResourceNoSecondaryCommander:
                    self.set_text(insert="Remove secondary commander")
                    self.tap(473, 501, 0.5)

                if not self.bot.config.randomTroops:
                    # select saves
                    self.select_save_army()

                match_button_pos = self.gui.check_any(ImagePathAndProps.TROOPS_MATCH_BUTTON_IMAGE_PATH.value)[2]
                self.set_text(insert="March")
                self.tap(match_button_pos[0], match_button_pos[1], 1)
                repeat_count = 0
                self.swipe(300, 720, 400, 360, 1)

        except Exception as e:
            traceback.print_exc()
            return next_task
        return next_task

    def get_min_resource(self):
        self.tap(725, 20, 1)
        result = self.gui.resource_amount_image_to_string()
        self.set_text(
            insert="\nFood: {}\nWood: {}\nStone: {}\nGold: {}\n".format(result[0], result[1], result[2], result[3]))

        ratio = [
            self.bot.config.gatherResourceRatioFood,
            self.bot.config.gatherResourceRatioWood,
            self.bot.config.gatherResourceRatioStone,
            self.bot.config.gatherResourceRatioGold
        ]

        ras = sum(ratio)
        res = sum(result)

        diff = []
        for i in range(4):
            diff.append((ratio[i] / ras) - ((result[i] if result[i] > -1 else 0) / res))

        m = 0
        for i in range(len(result)):
            if diff[m] < diff[i]:
                m = i
        return m

    def check_query_space(self):
        found, _, _ = self.gui.check_any(ImagePathAndProps.HAS_MATCH_QUERY_IMAGE_PATH.value)
        curr_q, max_q = self.gui.match_query_to_string()
        if curr_q is None:
            return self.max_query_space
        return max_q - curr_q

    def select_save_army(self):
        for t in [1, 2, 3, 4, 5]:
            if self.select_save_blue(t):
                return
            else:
                super().set_text(insert="Save {} not found".format(t))
        raise RuntimeError('Save not found')

    def select_save_blue(self, n):
        image = None
        if n == 1:
            image = ImagePathAndProps.UNSELECT_BLUE_ONE_SAVE_BUTTON_IMAGE_PATH
        elif n == 2:
            image = ImagePathAndProps.UNSELECT_BLUE_TWO_SAVE_BUTTON_IMAGE_PATH
        elif n == 3:
            image = ImagePathAndProps.UNSELECT_BLUE_THREE_SAVE_BUTTON_IMAGE_PATH
        elif n == 4:
            image = ImagePathAndProps.UNSELECT_BLUE_FOUR_SAVE_BUTTON_IMAGE_PATH
        elif n == 5:
            image = ImagePathAndProps.UNSELECT_BLUE_FIVE_SAVE_BUTTON_IMAGE_PATH
        if image is not None:
            return self.select_save_blue_image(image)
        return False

    def select_save_blue_image(self, image):
        has_save_btn, _, save_btn_pos = self.gui.check_any(image.value)

        if has_save_btn:
            return self.tap_on_save_btn(save_btn_pos, image)
        else:
            super().set_text(insert='Save not found')
            return False

    def tap_on_save_btn(self, pos, image):
        _x, _y = pos
        super().tap(_x, _y, 1)
        is_save_unselect, _, _ = self.gui.check_any(image.value)
        if is_save_unselect:
            super().set_text(insert='Commander not in city, stop current task')
            return False
        return True
